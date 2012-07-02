import logging, os, random
from zc.buildout import UserError, easy_install
from zc.recipe.egg import Egg


SETTINGS_TEMPLATE = '''
from %(settings_module)s import *

SECRET_KEY = "%(secret)s"

%(settings_override)s
'''

SCRIPT_TEMPLATES = {
    'wsgi': easy_install.script_header + '''

%(relative_paths_setup)s
import sys
sys.path[0:0] = [
    %(path)s,
    ]
%(initialization)s
import os
try:
    from django.core.wsgi import get_wsgi_application
    IS_14_PLUS = True
except ImportError:
    from django.core.handlers.wsgi import WSGIHandler
    IS_14_PLUS = False

os.environ['DJANGO_SETTINGS_MODULE'] = "%(module_name)s%(attrs)s"


def app_factory(global_config, **local_config):
    """This function wraps our simple WSGI app so it
    can be used with paste.deploy"""
    if IS_14_PLUS:
        return get_wsgi_application()
    else:
        return WSGIHandler()

application = app_factory(%(arguments)s)
''',
    'manage': easy_install.script_header + '''

%(relative_paths_setup)s
import sys
sys.path[0:0] = [
    %(path)s,
    ]
%(initialization)s
import os
try:
    from django.core.management import execute_from_command_line
    IS_14_PLUS = True
except ImportError:
    from django.core.management import ManagementUtility
    IS_14_PLUS = False

os.environ['DJANGO_SETTINGS_MODULE'] = "%(module_name)s%(attrs)s"
if IS_14_PLUS:
    execute_from_command_line(%(arguments)s)
else:
    utility = ManagementUtility(%(arguments)s)
    utility.execute()
'''
}


class Recipe(object):
    wsgi_file = 'wsgi.py'
    settings_file = 'settings.py'
    sites_default = 'sites'
    site_settings_template = '%(name)s_site_config'
    secret_cfg = '.secret.cfg'

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(name)
        self.options['location'] = os.path.join(
            self.buildout['buildout']['parts-directory'], self.name
        )
        self.options.setdefault('extra-paths', '')
        self.options.setdefault('environment-vars', '')
        self.options.setdefault('sites-directory', self.sites_default)
        self.options.setdefault('settings-override', '')
        self.options.setdefault('settings-file', self.settings_file)
        self.options.setdefault('wsgi-file', self.wsgi_file)
        self.options.setdefault('manage-py-file', 'django')
        self.eggs = [ ]
        if 'eggs' in self.buildout['buildout']:
            self.eggs.extend(self.buildout['buildout']['eggs'].split())
        if 'eggs' in self.options:
            self.eggs.extend(self.options['eggs'].split())
        self.working_set = None
        self.extra_paths = [ self.options['location'] ]
        sites_path = os.path.join(
            self.buildout['buildout']['directory'],
            self.options['sites-directory']
        )
        if os.path.isdir(sites_path):
            self.extra_paths.append(sites_path)
        if os.path.isdir(sites_path) and 'settings-module' not in self.options:
            # Check if the user has created a module %(name)s_config
            settings_module = self.site_settings_template % {
                'name': self.name
            }
            settings_module_path = os.path.join(sites_path, settings_module)
            initpy = os.path.join(settings_module_path, '__init__.py')
            settingspy = os.path.join(settings_module_path, 'settings.py')
            if os.path.isdir(settings_module_path) and \
                    os.path.isfile(initpy) and os.path.isfile(settingspy):
                self.options.setdefault('settings-module',
                                        '%s.settings' % settings_module)
        self.extra_paths.extend(self.options['extra-paths'].split())
        self.secret_key = None

    def setup_working_set(self):
        egg = Egg(
            self.buildout, 'Django', self.options
        )
        self.working_set = egg.working_set(self.eggs)

    def setup_secret(self):
        secret_file = os.path.join(
            self.buildout['buildout']['directory'],
            self.secret_cfg
        )
        if os.path.isfile(secret_file):
            stream = open(secret_file, 'rb')
            data = stream.read().decode('utf-8').strip()
            stream.close()
            self.logger.debug("Read secret: %s" % data)
        else:
            stream = open(secret_file, 'wb')
            chars = u'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            data = u''.join([random.choice(chars) for __ in range(50)])
            stream.write(data.encode('utf-8')+u"\n")
            stream.close()
            self.logger.debug(
                "Generated secret: %s (and written to %s)" % (data, secret_file)
            )
        self.secret_key = data
        return secret_file

    def setup_module_file(self, module, name, data):
        with open(os.path.join(module, name), 'wb') as stream:
            stream.write(data)

    def get_settings(self, static_directory=None, media_directory=None):
        if 'settings-module' not in self.options:
            raise UserError(
                ("You should specify 'settings-module' in %(name)s "
                 "or create a module named '"+self.site_settings_template+"' "
                 "in '%(sites)s' with a 'settings.py' file in it") % {
                    'name': self.name,
                    'sites': self.options['sites-directory']
                 }
            )
        settings_override = self.options['settings-override']
        if static_directory is not None:
            settings_override += '\nSTATIC_ROOT = "%s"\n' % (
                static_directory,
            )
        if media_directory is not None:
            settings_override += '\nMEDIA_ROOT = "%s"\n' % (
                media_directory,
            )
        return SETTINGS_TEMPLATE % {
            'settings_module': self.options['settings-module'],
            'secret': self.secret_key,
            'settings_override': settings_override
        }

    def setup_directories(self):
        result = []
        for directory in [ 'static-directory', 'media-directory' ]:
            result.append(None)
            if directory in self.options:
                path = os.path.join(
                    self.buildout['buildout']['directory'],
                    self.options[directory]
                )
                if not os.path.isdir(path):
                    os.makedirs(path)
                result[-1] = path
        return result

    def get_initialization(self):
        # The initialization code is expressed as a list of lines
        initialization = []

        # Gets the initialization code: the tricky part here is to preserve
        # indentation.
        # Since buildout does totally waste whitespace, if one wants to
        # preserve indentation must prefix its lines with '>>> ' or '... '
        raw_value = self.options.get('initialization', '')
        is_indented = False
        indentations = ('>>> ', '... ')
        for line in raw_value.splitlines():
            if line != "":
                if len(initialization) == 0:
                    if line.startswith(indentations[0]):
                        is_indented = True
                else:
                    if is_indented and not line.startswith(indentations[1]):
                        raise UserError(
                            ("Line '%s' should be indented "
                             "properly but is not") % line
                        )
                if is_indented:
                    line = line[4:]
                initialization.append(line)

        # Gets the environment-vars option and generates code to set the
        # enviroment variables via os.environ
        environment_vars = []
        for line in self.options.get('environment-vars', '').splitlines():
            line = line.strip()
            if len(line) > 0:
                try:
                    var_name, raw_value = line.split(' ', 1)
                except ValueError:
                    raise RuntimeError(
                        "Bad djc.recipe2 environment-vars contents: %s" % line
                    )
                environment_vars.append(
                    'os.environ["%s"] = r"%s"' % (
                        var_name,
                        raw_value.strip()
                    )
                )
        if len(environment_vars) > 0:
            initialization.append("import os")
            initialization.extend(environment_vars)

        if len(initialization) > 0:
            return "\n"+"\n".join(initialization)+"\n"
        return ""

    def create_script(self, name, path, settings, template, arguments):
        """Create arbitrary script.

        This script will also include the eventual code found in
        ``initialization`` and will also set (via ``os.environ``) the
        environment variables found in ``environment-vars``
        """

        self.logger.info(
            "Creating script at %s" % (os.path.join(path, name),)
        )
        settings = settings.rsplit(".", 1)
        module = settings[0]
        attrs = ""
        if len(settings) > 1:
            attrs = "." + settings[1]

        old_script_template = easy_install.script_template
        easy_install.script_template = template
        script = easy_install.scripts(
            reqs=[(name, module, attrs)],
            working_set=self.working_set[1],
            executable=self.options['executable'],
            dest=path,
            extra_paths=self.extra_paths,
            initialization=self.get_initialization(),
            arguments=str(arguments)
        )
        easy_install.script_template = old_script_template
        return script

    def setup_manage_script(self, settings):
        arguments = "sys.argv"
        return self.create_script(
            self.options['manage-py-file'],
            self.buildout['buildout']['bin-directory'],
            settings,
            SCRIPT_TEMPLATES['manage'],
            arguments
        )

    def setup_wsgi_script(self, module_path, settings):
        arguments = "global_config={}"
        return self.create_script(
            self.options['wsgi-file'],
            module_path,
            settings,
            SCRIPT_TEMPLATES['wsgi'],
            arguments
        )

    def setup(self, static_directory=None, media_directory=None):
        part_module = '%s_part_site' % self.name
        part_module_path = os.path.join(self.options['location'], part_module)
        settings_module = "%s.%s" % (
            part_module,
            os.path.splitext(self.options['settings-file'])[0]
        )
        if not os.path.exists(part_module_path):
            os.makedirs(part_module_path)
        self.setup_module_file(part_module_path, '__init__.py', "#\n")
        self.setup_module_file(
            part_module_path,
            self.options['settings-file'],
            self.get_settings(static_directory, media_directory)
        )
        self.setup_wsgi_script(part_module_path, settings_module)
        files = [ self.options['location'] ]
        files.extend(self.setup_manage_script(settings_module))
        return files

    def install(self):
        files = []
        self.setup_working_set()
        # The .secret.cfg file is not reported so it doesn't get deleted
        self.setup_secret()
        static_directory, media_directory = self.setup_directories()
        # static and media are not added to files so that updates
        # won't delete them, nor reinstallations of parts
        files.extend(self.setup(static_directory, media_directory))
        return tuple(files)

    update = install
