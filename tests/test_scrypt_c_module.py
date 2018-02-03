from sys import version_info, exit

if ((version_info > (3, 2, 0, 'final', 0)) or
        (version_info > (2, 7, 0, 'final', 0) and
         version_info < (3, 0, 0, 'final', 0))):
    import unittest as testm
else:
    try:
        import unittest2 as testm
    except ImportError:
        print("Please install unittest2 to run the test suite")
        exit(-1)


class TestScryptCModule(testm.TestCase):
    def test_import_module(self):
        """Test importing the _scrypt module"""

        import _scrypt

        self.assertTrue(_scrypt)
