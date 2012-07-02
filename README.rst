.. contents::

This recipe allows you to setup a Django project through `zc.buildout`_.

Usage
*****

In order to use this recipe, create a buildout as follows::

    [buildout]
    parts =
        myproject

    [myproject]
    recipe = djc.recipe2

And then create a python module in ``sites/<part_name>_site_config``
containing the ``settings.py`` file.

The buildout will take care of creating a manage script at ``bin/django``
and a *WSGI* app to serve the project in production
at ``parts/myproject/myproject_part_site/wsgi.py``.

In our example, this will result in the following file structure::

    <buildout_root>
    |
    |- bin
    |  |
    |  |- ...
    |  |
    |  |- django # the manage.py script
    |
    |- ...
    |
    |- parts
    |  |
    |  |- myproject
    |     |
    |     |- myproject_part_site # put this on PYTHONPATH when serving via WSGI
    |        |
    |        |- __init__.py
    |        |
    |        |- ...
    |        |
    |        |- wsgi.py # WSGI app and paster app factory
    |
    |- ...
    |
    |- sites
    |  |
    |  |- myproject_site_config
    |     |
    |     |- __init__.py # void
    |     |
    |     |- settings.py # your settings here
    |
    |- ...

For all the options and detailed documentation, see below.

Running tests
*************

The ``recipe.rst`` file located within the package also acts as main doctest.

To run the tests, check out the source,
and then bootstrap and run the buildout::

    $ python bootstrap.py
    $ bin/buildout

If it's a fresh checkout you should also run::

    $ ./makecache.sh

This command should be run just once after checking out:
it will download certain packages needed for the tests
so that they can run offline.

It should also be re-run if ``makecache.sh`` has changed.

Then you can run the tests using::

    $ bin/test

Links
*****

- Code repository: http://github.com/abstract-open-solutions/djc.recipe2
- Discussions at https://groups.google.com/group/djcrecipe
- Comments and questions at info@abstract.it
- Build status: .. image:: https://secure.travis-ci.org/simonedeponti/djc.recipe2.png

.. _`zc.buildout`: http://www.buildout.org/

