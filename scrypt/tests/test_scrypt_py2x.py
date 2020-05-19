# -*- coding: utf-8 -*-

from sys import version_info, exit
import scrypt
import unittest as testm


@testm.skipIf(version_info > (3, 0, 0, 'final', 0), "Tests for Python 2 only")
class TestScryptForPython2(testm.TestCase):

    def setUp(self):
        self.input = "message"
        self.password = "password"
        self.unicode_text = '\xe1\x93\x84\xe1\x93\x87\xe1\x95\x97\xe1\x92\xbb\xe1\x92\xa5\xe1\x90\x85\xe1\x91\xa6'.decode('utf-8')

    def test_py2_encrypt_fails_on_unicode_input(self):
        """Test Py2 encrypt raises TypeError when Unicode input passed"""
        self.assertRaises(TypeError, lambda: scrypt.encrypt(self.unicode_text, self.password))

    def test_py2_encrypt_fails_on_unicode_password(self):
        """Test Py2 encrypt raises TypeError when Unicode password passed"""
        self.assertRaises(TypeError, lambda: scrypt.encrypt(self.input, self.unicode_text))

    def test_py2_encrypt_returns_string(self):
        """Test Py2 encrypt returns str"""
        e = scrypt.encrypt(self.input, self.password, 0.1)
        self.assertTrue(isinstance(e, str))

    def test_py2_decrypt_returns_string(self):
        """Test Py2 decrypt returns str"""
        s = scrypt.encrypt(self.input, self.password, 0.1)
        m = scrypt.decrypt(s, self.password)
        self.assertTrue(isinstance(m, str))

    def test_py2_hash_returns_string(self):
        """Test Py2 hash return str"""
        h = scrypt.hash(self.input, self.password)
        self.assertTrue(isinstance(h, str))


if __name__ == "__main__":
    testm.main()
