from sys import version_info, exit
import unittest as testm


class TestScryptCModule(testm.TestCase):
    def test_import_module(self):
        """Test importing the _scrypt module"""

        import _scrypt

        self.assertTrue(_scrypt)
