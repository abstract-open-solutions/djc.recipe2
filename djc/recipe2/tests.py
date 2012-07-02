import unittest, os, shutil
from zc.buildout import testing
from zope.testing import doctest, renormalizing


optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)


def isdir(*path):
    return os.path.isdir(os.path.join(*path))


def isfile(*path):
    return os.path.isfile(os.path.join(*path))


def copytree(src, dst):
    shutil.copytree(
        os.path.join(*src),
        os.path.join(*dst)
    )


def copy_index():
    index_base = os.environ['buildout-testing-index-url'][len('file://'):]
    cache_base = os.path.join(os.path.dirname(__file__), '..', '..',
                              'pkg-cache')
    cache_base = os.path.normpath(cache_base)
    for file in os.listdir(cache_base):
        shutil.copyfile(
            os.path.join(cache_base, file),
            os.path.join(index_base, file)
        )


def setUp(test):
    testing.buildoutSetUp(test)
    test.globs['isdir'] = isdir
    test.globs['isfile'] = isfile
    test.globs['copytree'] = copytree
    copy_index()
    testing.install_develop('djc.recipe2', test)


def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'recipe.rst',
                setUp=setUp,
                tearDown=testing.buildoutTearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        testing.normalize_path,
                        ]),
                ),
            ))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

