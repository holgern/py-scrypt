from sys import version_info, exit

from .test_scrypt import TestScrypt, TestScryptHash
from .test_scrypt_c_module import TestScryptCModule
from .test_scrypt_py2x import TestScryptForPython2
from .test_scrypt_py3x import TestScryptForPy3

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
