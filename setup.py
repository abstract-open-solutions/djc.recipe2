# -*- coding: utf-8 -*-
"""Setup module for of djc.recipe2
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '2.2.dev0'

long_description = (
    read('README.rst')
    + '\n' +
    'Detailed documentation\n'
    '**********************\n'
    + '\n' +
    read('djc', 'recipe2', 'recipe.rst')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.rst')
)
entry_point = 'djc.recipe2.recipe:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'zc.buildout']

setup(name='djc.recipe2',
      version=version,
      description="A Django buildout recipe",
      long_description=long_description,
      # Get more strings
      # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
      ],
      keywords='',
      author='Simone Deponti',
      author_email='simone.deponti@abstract.it',
      url='http://github.com/abstract-open-solutions/djc.recipe2',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['djc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg'
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'djc.recipe2.tests.test_suite',
      entry_points=entry_points,
      )
