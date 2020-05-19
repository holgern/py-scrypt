from sys import version_info, exit
import unittest as testm
from .test_scrypt import TestScrypt, TestScryptHash
from .test_scrypt_c_module import TestScryptCModule
from .test_scrypt_py2x import TestScryptForPython2
from .test_scrypt_py3x import TestScryptForPy3


def all_tests():
    suite = testm.TestSuite()
    loader = testm.TestLoader()

    test_classes = [
        TestScrypt,
        TestScryptCModule,
        TestScryptHash,
        TestScryptForPython2,
        TestScryptForPy3,
    ]

    for cls in test_classes:
        tests = loader.loadTestsFromTestCase(cls)
        suite.addTests(tests)

    return suite
