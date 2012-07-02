Basic usage
===========

The basic thing you have to do in order to have a Django_ site
is to provide it some configuration.

In Django_, configuration is achieved by creating a set of global variables
in a `settings module`_ and letting Django_ know which is the
settings module to use.

This recipe, in its basic functioning, adopts a *convention over configuration*
approach to the matter.

.. note::
   It is also possible to use other approaches,
   as explained in `External settings`_.

Therefore, all the configurations for all the Django_ parts in your buildout **must** be places within a ``sites`` directory located in your buildout root.

Within this directory, a *python module* (create an empty ``__init__.py``!)
named ``<part_name>_site_config`` must be created, and within it,
a ``settings.py`` file containing your settings must be placed.

For example, if our Django_ part is named ``myproject``
(we are referring to the buildout part name here),
we would do the following::

    >>> mkdir('sites')
    >>> mkdir('sites', 'myproject_site_config')
    >>> write('sites', 'myproject_site_config', '__init__.py',
    ...       '#\n')
    >>> write('sites', 'myproject_site_config', 'settings.py', '''
    ... SPAM = 'eggs'
    ... ''')

Okay, that settings file is not exactly a good one,
but it will suffice for now as an example.

Let's now create our buildout and run it::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>

As you can see, the part for now contains only the recipe, as it will work
*out of the box* without further meddling if we adhere to its conventions.

Let's see what the buildout did. To start with, it created a ``django`` binary
within ``bin`` that is the equivalent of Django's ``manage.py``
(which means you can invoke it exactly like you would with ``manage.py``)::

    >>> ls('bin')
    -  buildout
    -  django

.. note::
   Ofcourse, since the binary name is always ``django``,
   this will cause problems if you have more than one Django_ part
   in your buildout:
   this is solved by the `manage-py-file`_ option
   explained in the `Options reference`_.

The next thing the buildout did is to create yet another python module
(in ``parts/<part_name>``)::

    >>> ls('parts', 'myproject')
    d  myproject_part_site
    >>> ls('parts', 'myproject', 'myproject_part_site')
    -  __init__.py
    -  settings.py
    -  wsgi.py

**Another** python module?

Yes, because unlike the first one, this is under buildout's strict control,
and generated each time you run ``bin/buildout``
(therefore, it is a *very bad idea* to edit those files,
because your changes won't be kept).

In this module, we have again a ``settings.py`` file, plus a ``wsgi.py`` file.
We will look at the latter in more detail in `Going production`_: the first,
instead, is the actual settings module that will be loaded by Django_.

So what about the settings we defined earlier? Do not fear,
because the buildout created ``settings.py`` will import the module you wrote
and add to it the ``SECRET_KEY`` setting::

    >>> cat('parts', 'myproject', 'myproject_part_site', 'settings.py')
    from myproject_site_config.settings import *
    <BLANKLINE>
    SECRET_KEY = "..."
    <BLANKLINE>
    <BLANKLINE>

This (slightly convoluted) setup exists because a poorly chosen ``SECRET_KEY``
can become a security problem (and quite a big one, for pathological cases).

Since it's way too easy to pick a simple one
(maybe because we can't be bothered to come up with a decent one)
and even more easy to forget to change it between
development and production environment,
this recipe generates a long, random key for you.

This way you can safely omit ``SECRET_KEY`` within your ``settings.py`` file
and at the same time be completely secure.

This key is generated only once and is kept
through the various runs of ``bin/buildout``.
This is possible because the recipe will first look
whether a ``.secret.cfg`` file exists in the buildout root:
if it exists, it will read it and extract the key from there
(the file contents are the key itself and a newline).
If it doesn't exist, it will generate a new key and write it there.
Therefore, as long as a ``.secret.cfg`` file exists,
the recipe will use the same key throughout the various runs
of ``bin/buildout``.

Proof of the fact is that a ``.secret.cfg`` file exists in our buildout::

    >>> isfile('.secret.cfg')
    True

Complete example
----------------

Let's now put into our settings file (``myproject_site_config/settings.py``)
some more sane values::

    >>> write('sites', 'myproject_site_config', 'settings.py', '''
    ... DATABASES = {
    ...     'default': {
    ...         'ENGINE': 'django.db.backends.sqlite3',
    ...         'NAME': 'storage.db'
    ...     }
    ... }
    ... TIME_ZONE = 'Europe/Rome'
    ... ''')

Now, in order for these settings to take effect,
we don't have to re-run buildout,
as the import that the generated file does will pick them up::

    >>> print system('bin/django diffsettings')
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'storage.db'}}
    SECRET_KEY = '...'
    SETTINGS_MODULE = 'myproject_part_site.settings'  ###
    TIME_ZONE = 'Europe/Rome'

Seems like it worked!

We decided to put the database in a *SQLite* file named ``storage.db``,
which currently doesn't exist::

    >>> isfile('storage.db')
    False

Let's now tell Django_ to create the database::

    >>> print system('bin/django syncdb --noinput')
    Creating tables ...
    Installing custom SQL ...
    Installing indexes ...
    Installed 0 object(s) from 0 fixture(s)
    <BLANKLINE>

And we will see that the database has been created::

    >>> isfile('storage.db')
    True

Debug mode
----------

We can now start developing but, sooner or later,
we'll recognize that we haven't set ``DEBUG = True``,
which is fundamental `if your name is not Donald Knuth`_.

We could add it straight away in ``myproject_site_config/settings.py``,
but that might cause problems when we're `Going production`_,
because you definitely want to have ``DEBUG`` and its sisters off
when you're out in the open.

Therefore, another option that we have is to do the following::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... settings-override =
    ...     DEBUG = True
    ...     TEMPLATE_DEBUG = True
    ... ''')

Anything that we put in ``settings-override`` will be appended
at the end of the buildout-generated ``settings.py``
(treated as a string, so beware that no correctness checking
is performed).
This allows us to quickly differentiate production and development buildouts
without having the need to come up with two different ``settings.py`` files
(one for production and one for development).

If we re-run the buildout and look at the results,
we will see that we are now in debug mode::

    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> cat('parts', 'myproject', 'myproject_part_site', 'settings.py')
    from myproject_site_config.settings import *
    <BLANKLINE>
    SECRET_KEY = "..."
    <BLANKLINE>
    DEBUG = True
    TEMPLATE_DEBUG = True
    <BLANKLINE>
    >>> print system('bin/django diffsettings')
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'storage.db'}}
    DEBUG = True
    SECRET_KEY = '...'
    SETTINGS_MODULE = 'myproject_part_site.settings'  ###
    TEMPLATE_DEBUG = True
    TIME_ZONE = 'Europe/Rome'

.. note::
   Since this gets appended to the file, be careful that
   if you do define *and* reference ``DEBUG`` (or any other variable)
   within the ``settings.py`` file in your full control,
   our setting it *afterwards* will not affect its value
   within *your* ``settings.py``.
   So if in your ``settings.py`` you do ``DEBUG = False``
   and ``FOOBAR = False``, ``FOOBAR`` will always be false.

Of course, this is not limited to ``DEBUG``, you can use it for example
to override the ``DATABASES``, ``LOGGING`` and ``CACHES`` settings
in the production environment without having to create
a whole new ``settings.py`` file.

.. note::
   Due to buildout's limitations, indentation of ``settings-override``
   is completely lost. Therefore don't do ``if`` or more complex stuff:
   if you need to, check out `Advanced usage`_

Going production
----------------

As we saw above, if our development setup doesn't differ too much
from our production setup
(save for the fact that we use a real cache, a more complex RDBMS, etc)
then we can use ``settings-override`` to manage it::

    >>> mkdir('var')
    >>> mkdir('var', 'log')
    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... settings-override =
    ...     DATABASES = {
    ...         'default': {
    ...             'ENGINE': 'django.db.backends.postgresql_psycopg2',
    ...             'HOST': 'localhost',
    ...             'PORT': '5432',
    ...             'NAME': 'mydb',
    ...             'USER': 'mydb',
    ...             'PASSWORD': 'secret'
    ...         }
    ...     }
    ...     CACHES = {
    ...         'default': {
    ...             'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    ...             'LOCATION': '127.0.0.1:11211',
    ...         }
    ...     }
    ...     LOGGING = {
    ...         'version': 1,
    ...         'disable_existing_loggers': True,
    ...         'root': { 'level': 'WARNING', 'handlers': ['logfile'], },
    ...         'formatters': {
    ...             'verbose': {
    ...                 'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    ...             },
    ...         },
    ...         'handlers': {
    ...             'logfile': {
    ...                 'level': 'ERROR',
    ...                 'class': 'logging.handlers.RotatingFileHandler',
    ...                 'filename': 'var/log/myproject.log',
    ...                 'maxBytes': 1024,
    ...                 'backupCount': 3,
    ...             },
    ...             'console': {
    ...                 'level': 'DEBUG',
    ...                 'class': 'logging.StreamHandler',
    ...                 'formatter': 'verbose'
    ...             }
    ...         },
    ...         'loggers': {
    ...             'django.db.backends': {
    ...                 'level': 'ERROR',
    ...                 'handlers': ['console'],
    ...                 'propagate': False,
    ...             },
    ...         },
    ...     }
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> print system('bin/django diffsettings')
    CACHES = ...
    DATABASES = ...
    LOGGING = ...
    SECRET_KEY = '...'
    SETTINGS_MODULE = 'myproject_part_site.settings'  ###
    TIME_ZONE = 'Europe/Rome'

This is actually a quite complete (albeit basic) production example,
and it can still be managed quite well within the buildout.

If we do have more complex cases, however,
it's probably better to use `External settings`_.

Changing the binary name
------------------------

As we have said before, the name of the generated binary is always ``django``,
without any suffix or prefix.

The rational for this choice is the following:

  #. Having the script named ``django`` and it being the same
     no matter how you call the buildout part simplifies
     getting into development a lot
     (it's always ``bin/django runserver`` after you run the buildout,
     and you don't have to go and look how it is named
     in that particular buildout)

  #. Since in production you will just configure your *WSGI* server
     to use multiple processes, there are very few reasons
     to have multiple Django_ parts in your buildout

But if you really need to have multiple parts,
the default behaviour will have one part overwrite the other's script.
That's when you need to use the `manage-py-file`_ option,
which allows you to provide a different name
(say, ``django1`` and ``django2``) for the manage script.

First we start by copying the settings of our sample project
to two ned different locations, ``myproject1`` and ``myproject2``::

    >>> copytree(['sites', 'myproject_site_config'],
    ...          ['sites', 'myproject1_site_config'])
    >>> copytree(['sites', 'myproject_site_config'],
    ...          ['sites', 'myproject2_site_config'])

Then we write a buildout that has *two* parts,
``myproject1`` and ``myproject2``, and run it::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject1
    ...     myproject2
    ...
    ... [myproject1]
    ... recipe = djc.recipe2
    ... manage-py-file = django1
    ...
    ... [myproject2]
    ... recipe = djc.recipe2
    ... manage-py-file = django2
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject1.
    ...
    Installing myproject2.
    ...
    <BLANKLINE>

And we will see that it has created two distinct scripts::

    >>> ls('bin')
    -  buildout
    -  django1
    -  django2


Advanced usage
==============

Custom initialization
---------------------

Sometimes, you need to do some magic before Django_ loads everything,
in order to use certain features.

For example, Pinax_, a very well known social site framework based on Django_,
needs you to perform certain ``sys.path`` magic before initialization.

This kind of customization can be done in two ways:

  #. By performing those in ``settings.py``
  #. By altering the manage script (and the *WSGI* one, too)

The first choice might look simpler but it actually hides much more complexity
than it is initially visible.
The latter is better but, since the script is generated by buildout,
we cannot simply edit that file.

Before looking at how you actually do it, let's make a premise:
we can divide this initialization stuff in two main groups.

The first and more common group is when you simply need
to set an environment variable: while this can be achieved
by doing ``$ MYVAR=value bin/django``, it's not exactly handy in the long run.

And here comes `environment-vars`_ to the rescue!

Let's look at a concrete example: running Django_ on `Google App Engine`_.
`Google App Engine`_ requires you to have a ``GOOGLE_APPENGINE_PROJECT_ROOT``
environment variable set, or nothing will work.

Therefore, in order to add it we would write our buildout as follows,
with a list of variables and values (separated by space)
for each environment variable we want to set::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... environment-vars =
    ...     GOOGLE_APPENGINE_PROJECT_ROOT /my/path
    ... ''')

And after running it, we can see that the script correctly initializes
the environment variable::

    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> cat('bin', 'django')
    #!...
    <BLANKLINE>
    ...
    <BLANKLINE>
    import os
    os.environ["GOOGLE_APPENGINE_PROJECT_ROOT"] = r"/my/path"
    <BLANKLINE>
    ...
    <BLANKLINE>
    os.environ['DJANGO_SETTINGS_MODULE'] = "myproject_part_site.settings"
    if IS_14_PLUS:
        execute_from_command_line(sys.argv)
    else:
        utility = ManagementUtility(sys.argv)
        utility.execute()

For the second case, the `initialization`_ option is provided:
this allows you to write (in a format similar to doctest)
the python code that you need to be executed before Django_ starts.

.. note::
   The slightly funny *doctest syntax* of this option is to overcome
   a shortcoming of buildout that will otherwise completely lose indentation.

Let's see how we would make sure that Django_ won't start at all
if ``1 != 1``::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... initialization =
    ...     >>> if 1 != 1:
    ...     ...     raise RuntimeError("I can't run on quantum computers")
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> cat('bin', 'django')
    #!...
    <BLANKLINE>
    ...
    <BLANKLINE>
    if 1 != 1:
        raise RuntimeError("I can't run on quantum computers")
    <BLANKLINE>
    ...
    <BLANKLINE>
    os.environ['DJANGO_SETTINGS_MODULE'] = "myproject_part_site.settings"
    if IS_14_PLUS:
        execute_from_command_line(sys.argv)
    else:
        utility = ManagementUtility(sys.argv)
        utility.execute()

.. note::
   I really couldn't come up with a better example
   that would work in tests without having to bring in loads of crap,
   but I can assure you this feature **is** useful. Really.

Media and static
----------------

This is a bit of personal preference.
When developing upon work started by someone else,
I find it utterly irritating that the upload doesn't work because,
after checking out and running the buildout, I did not do ``$ mkdir media``.

Because:

  #. I'm getting old and I tend to forget that
  #. Sometimes it's not ``media``, but ``var/upload/mediafiles``
     or something else (yes, we programmers tend to express creativity
     in the most inopportune ways)

That's why I've added two options that, while not being on by default,
I wish you have turned on (atleast one of them)
if I have to work on your buildout.

The options are `media-directory`_ and `static-directory`_,
and their values are the path to the media root and the static root
respectively.
When they are set, the buildout will create them if they don't exist
and then append to the settings module the proper ``MEDIA_ROOT``
and ``STATIC_ROOT`` setting.

Let's see them in action. First we check that we don't have any
``static`` or ``media`` directory::

    >>> isdir('media')
    False
    >>> isdir('static')
    False

Then write and run the buildout::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... media-directory = media
    ... static-directory = static
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>

And then see that we have the directories and the settings::

    >>> isdir('media')
    True
    >>> isdir('static')
    True
    >>> print system('bin/django diffsettings')
    DATABASES = ...
    MEDIA_ROOT = '...'
    SECRET_KEY = '...'
    SETTINGS_MODULE = 'myproject_part_site.settings'  ###
    STATIC_ROOT = '...'
    TIME_ZONE = 'Europe/Rome'

Obviously, you do not need to use them together
but they can be used independently.

External settings
-----------------

Sometimes, one file for all the settings just ain't enough,
or it might turn out that `settings-override`_ is not quite handy for you.

That's why this recipe allows you to use as a settings module anything
that's in in ``sys.path``.

For example, suppose we want to put our production settings
in a file on its own: we might then create a file
named ``sites/myproject_site_config/production.py``
and use that as settings module.

First, let's create the file::

    >>> write('sites', 'myproject_site_config', 'production.py', '''
    ... from .settings import *
    ... TIME_ZONE = 'Europe/London'
    ... ''')

Then we tell the buildout to use the module
``myproject_site_config.production`` as settings module
instead of the default one, through the `settings-module`_ option::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... settings-module = myproject_site_config.production
    ... ''')

.. note::
   The module can be anything in ``sys.path``, but here we reused the
   same directory because whenever `sites-directory`_ exists
   and regardless of what's in it, it is put on ``sys.path``.
   You can ofcourse have the settings module in your project egg
   or whatever else.

And we can then run the buildout and see what happened::

    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> print system('bin/django diffsettings')
    DATABASES = ...
    SECRET_KEY = '...'
    SETTINGS_MODULE = 'myproject_part_site.settings'  ###
    TIME_ZONE = 'Europe/London'

And as you can see, the changes took effect.

Options reference
=================

eggs
----

A list of eggs that the generated scripts must have access to.
This typically includes your application eggs and their dependencies,
if the latter are not explicited within the ``setup.py`` file.

They can be explicited either as a part option::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... eggs = django-gravatar2
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> cat('bin', 'django')
    #...
    <BLANKLINE>
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '.../eggs/django_gravatar2-1.0.4-...egg',
        ...
        ]
    <BLANKLINE>
    ...

Or as a buildout option::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... eggs = django-gravatar2
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> cat('bin', 'django')
    #...
    <BLANKLINE>
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '.../eggs/django_gravatar2-1.0.4-...egg',
        ...
        ]
    <BLANKLINE>
    ...

Or both, and they will be merged::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... eggs = South
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... eggs = django-gravatar2
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> cat('bin', 'django')
    #...
    <BLANKLINE>
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        '.../eggs/django_gravatar2-1.0.4-...egg',
        '.../eggs/South-0.7.5-...egg',
        ...
        ]
    <BLANKLINE>
    ...

environment-vars
----------------

A list of environment variables to set before execution,
each separated by newline and in the format ``VAR_NAME value``.

See `Custom initialization`_ for an example.

extra-paths
-----------

A list of paths, separated by newline,
that should be added to ``sys.path`` before the code is executed
(allowing the discovery of custom modules).

For example::

    >>> mkdir('custom_modules')
    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... extra-paths =
    ...     custom_modules
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> cat('bin', 'django')
    #...
    <BLANKLINE>
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        ...
        '.../custom_modules',
        ]
    <BLANKLINE>
    ...

initialization
--------------

Python code, to be formatted like a doctest,
that is to be executed before any initialization happens.

See `Custom initialization`_ for an example.

manage-py-file
--------------

The name of the generated manage script in ``bin``.

See `Changing the binary name`_ for an example.

settings-file
-------------

The name of the generated settings file
(the one that's autogenerated by buildout at each run).

This option can be quite useful to avoid module name clashes::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... settings-file = configuration.py
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> print system('bin/django diffsettings')
    DATABASES = ...
    SECRET_KEY = '...'
    SETTINGS_MODULE = 'myproject_part_site.configuration'  ###
    TIME_ZONE = 'Europe/Rome'

settings-module
---------------

Loads a custom settings module instead of the conventional one.

See `External settings`_ for an example.

settings-override
-----------------

Specifies some settings (as python code) to be appended
to the auto-generated settings file and thus overriding the module-defined ones.

See `Debug mode`_ for an example.

sites-directory
---------------

Changes the default location of the conventional configuration location
(normally the ``sites`` directory).

It will be appended to ``sys.path``::

    >>> copytree(['sites'], ['mysites'])
    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... sites-directory = mysites
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> cat('bin', 'django')
    #...
    <BLANKLINE>
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
        ...
        '.../mysites',
        ]
    <BLANKLINE>
    ...

static-directory
----------------

Sets the location of ``STATIC_ROOT`` and creates it if missing.

See `Media and static`_.

media-directory
---------------

Same as `static-directory`_ for ``MEDIA_ROOT``.

wsgi-file
---------

Changes the name of the file that contains the *WSGI* application.

The purpose is similar to `settings-file`_::

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts =
    ...     myproject
    ...
    ... [myproject]
    ... recipe = djc.recipe2
    ... wsgi-file = wsgiapp.py
    ... ''')
    >>> print "$ bin/buildout\n", system(buildout)
    $ bin/buildout
    ...
    Installing myproject.
    ...
    <BLANKLINE>
    >>> ls('parts', 'myproject', 'myproject_part_site')
    -  __init__.py
    -  settings.py
    -  wsgiapp.py

.. _Django: https://djangoproject.com
.. _`settings module`: https://docs.djangoproject.com/en/dev/topics/settings/
.. _`if your name is not Donald Knuth`: http://www-cs-faculty.stanford.edu/~knuth/faq.html
.. _Pinax: http://pinaxproject.com/
.. _`Google App Engine`: https://developers.google.com/appengine/
