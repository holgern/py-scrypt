# -*- coding: utf-8 -*-

from sys import version_info, exit
import scrypt
import unittest as testm


@testm.skipIf(version_info < (3, 0, 0, 'final', 0), "Tests for Python 3 only")
class TestScryptForPy3(testm.TestCase):

    def setUp(self):
        self.input = "message"
        self.password = "password"
        self.byte_text = b'\xe1\x93\x84\xe1\x93\x87\xe1\x95\x97\xe1\x92\xbb\xe1\x92\xa5\xe1\x90\x85\xe1\x91\xa6'
        self.unicode_text = self.byte_text.decode('utf-8', "strict")

    def test_py3_encrypt_allows_bytes_input(self):
        """Test Py3 encrypt allows unicode input"""
        s = scrypt.encrypt(self.byte_text, self.password, 0.1)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(bytes(m.encode("utf-8")), self.byte_text)

    def test_py3_encrypt_allows_bytes_password(self):
        """Test Py3 encrypt allows unicode password"""
        s = scrypt.encrypt(self.input, self.byte_text, 0.1)
        m = scrypt.decrypt(s, self.byte_text)
        self.assertEqual(m, self.input)

    def test_py3_encrypt_returns_bytes(self):
        """Test Py3 encrypt return bytes"""
        s = scrypt.encrypt(self.input, self.password, 0.1)
        self.assertTrue(isinstance(s, bytes))

    def test_py3_decrypt_returns_unicode_string(self):
        """Test Py3 decrypt returns Unicode UTF-8 string"""
        s = scrypt.encrypt(self.input, self.password, 0.1)
        m = scrypt.decrypt(s, self.password)
        self.assertTrue(isinstance(m, str))

    def test_py3_hash_returns_bytes(self):
        """Test Py3 hash return bytes"""
        h = scrypt.hash(self.input, self.password)
        self.assertTrue(isinstance(h, bytes))


if __name__ == "__main__":
    testm.main()
