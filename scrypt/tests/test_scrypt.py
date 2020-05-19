# -*- coding: utf-8 -*-

from os import urandom
from os.path import dirname, abspath, sep
from sys import version_info, exit
from csv import reader
from binascii import a2b_hex, b2a_hex
import scrypt
import unittest as testm


class TestScrypt(testm.TestCase):

    def setUp(self):
        self.input = "message"
        self.password = "password"
        self.longinput = str(urandom(100000))
        self.five_minutes = 300.0
        self.five_seconds = 5.0
        self.one_byte = 1  # in Bytes
        self.one_megabyte = 1024 * 1024  # in Bytes
        self.ten_megabytes = 10 * self.one_megabyte
        base_dir = dirname(abspath(__file__)) + sep
        cvf = open(base_dir + "ciphertexts.csv", "r")
        ciphertxt_reader = reader(cvf, dialect="excel")
        self.ciphertexts = []
        for row in ciphertxt_reader:
            self.ciphertexts.append(row)
        cvf.close()
        self.ciphertext = a2b_hex(bytes(self.ciphertexts[1][5].encode('ascii')))

    def test_encrypt_decrypt(self):
        """Test encrypt for simple encryption and decryption"""
        s = scrypt.encrypt(self.input, self.password, 0.1)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt(self):
        """Test encrypt takes input and password strings as
        positional arguments and produces ciphertext"""
        s = scrypt.encrypt(self.input, self.password)
        self.assertEqual(len(s), 128 + len(self.input))

    def test_encrypt_input_and_password_as_keywords(self):
        """Test encrypt for input and password accepted as keywords"""
        s = scrypt.encrypt(password=self.password, input=self.input)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_missing_input_keyword_argument(self):
        """Test encrypt raises TypeError if keyword argument missing input"""
        self.assertRaises(TypeError, lambda: scrypt.encrypt(password=self.password))

    def test_encrypt_missing_password_positional_argument(self):
        """Test encrypt raises TypeError if second positional argument missing
        (password)"""
        self.assertRaises(TypeError, lambda: scrypt.encrypt(self.input))

    def test_encrypt_missing_both_required_positional_arguments(self):
        """Test encrypt raises TypeError if both positional arguments missing
        (input and password)"""
        self.assertRaises(TypeError, lambda: scrypt.encrypt())

    def test_encrypt_maxtime_positional(self):
        """Test encrypt maxtime accepts maxtime at position 3"""
        s = scrypt.encrypt(self.input, self.password, 0.01)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_maxtime_key(self):
        """Test encrypt maxtime accepts maxtime as keyword argument"""
        s = scrypt.encrypt(self.input, self.password, maxtime=0.01)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_maxmem_positional(self):
        """Test encrypt maxmem accepts 4th positional argument and exactly
        (1 megabyte) of storage to use for V array"""
        s = scrypt.encrypt(self.input, self.password, 0.01, self.one_megabyte)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_maxmem_undersized(self):
        """Test encrypt maxmem accepts (< 1 megabyte) of storage to use for V array"""
        s = scrypt.encrypt(self.input, self.password, 0.01, self.one_byte)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_maxmem_in_normal_range(self):
        """Test encrypt maxmem accepts (> 1 megabyte) of storage to use for V array"""
        s = scrypt.encrypt(self.input,
                           self.password,
                           0.01,
                           self.ten_megabytes)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_maxmem_keyword_argument(self):
        """Test encrypt maxmem accepts exactly (1 megabyte) of storage to use for
        V array"""
        s = scrypt.encrypt(self.input,
                           self.password,
                           maxmem=self.one_megabyte,
                           maxtime=0.01)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_maxmemfrac_positional(self):
        """Test encrypt maxmemfrac accepts 5th positional argument of 1/16 total
        memory for V array"""
        s = scrypt.encrypt(self.input, self.password, 0.01, 0, 0.0625)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_maxmemfrac_keyword_argument(self):
        """Test encrypt maxmemfrac accepts keyword argument of 1/16 total memory for
        V array"""
        s = scrypt.encrypt(self.input, self.password, maxmemfrac=0.0625,
                           maxtime=0.01)
        m = scrypt.decrypt(s, self.password)
        self.assertEqual(m, self.input)

    def test_encrypt_long_input(self):
        """Test encrypt accepts long input for encryption"""
        s = scrypt.encrypt(self.longinput, self.password, 0.1)
        self.assertEqual(len(s), 128 + len(self.longinput))

    def test_encrypt_raises_error_on_invalid_keyword(self):
        """Test encrypt raises TypeError if invalid keyword used in argument"""
        self.assertRaises(TypeError, lambda: scrypt.encrypt(self.input,
            self.password, nonsense="Raise error"))

    def test_decrypt_from_csv_ciphertexts(self):
        """Test decrypt function with precalculated combinations"""
        for row in self.ciphertexts[1:]:
            h = scrypt.decrypt(a2b_hex(bytes(row[5].encode('ascii'))), row[1])
            self.assertEqual(bytes(h.encode("ascii")), row[0].encode("ascii"))

    def test_decrypt_maxtime_positional(self):
        """Test decrypt function accepts third positional argument"""
        m = scrypt.decrypt(self.ciphertext, self.password, self.five_seconds)
        self.assertEqual(m, self.input)

    def test_decrypt_maxtime_keyword_argument(self):
        """Test decrypt function accepts maxtime keyword argument"""
        m = scrypt.decrypt(maxtime=1.0, input=self.ciphertext, password=self.password)
        self.assertEqual(m, self.input)

    def test_decrypt_maxmem_positional(self):
        """Test decrypt function accepts fourth positional argument"""
        m = scrypt.decrypt(self.ciphertext, self.password, self.five_minutes, self.ten_megabytes)
        self.assertEqual(m, self.input)

    def test_decrypt_maxmem_keyword_argument(self):
        """Test decrypt function accepts maxmem keyword argument"""
        m = scrypt.decrypt(maxmem=self.ten_megabytes, input=self.ciphertext, password=self.password)
        self.assertEqual(m, self.input)

    def test_decrypt_maxmemfrac_positional(self):
        """Test decrypt function accepts maxmem keyword argument"""
        m = scrypt.decrypt(self.ciphertext, self.password, self.five_minutes, self.one_megabyte, 0.0625)
        self.assertEqual(m, self.input)

    def test_decrypt_maxmemfrac_keyword_argument(self):
        """Test decrypt function accepts maxmem keyword argument"""
        m = scrypt.decrypt(maxmemfrac=0.625, input=self.ciphertext, password=self.password)
        self.assertEqual(m, self.input)

    def test_decrypt_raises_error_on_too_little_time(self):
        """Test decrypt function raises scrypt.error raised if insufficient time allowed for
        ciphertext decryption"""
        s = scrypt.encrypt(self.input, self.password, 0.1)
        self.assertRaises(scrypt.error,
                          lambda: scrypt.decrypt(s, self.password, .01))


class TestScryptHash(testm.TestCase):

    def setUp(self):
        self.input = "message"
        self.password = "password"
        self.salt = "NaCl"
        self.hashes = []
        base_dir = dirname(abspath(__file__)) + sep
        hvf = open(base_dir + "hashvectors.csv", "r")
        hash_reader = reader(hvf, dialect="excel")
        for row in hash_reader:
            self.hashes.append(row)
        hvf.close()

    def test_hash_vectors_from_csv(self):
        """Test hash function with precalculated combinations"""
        for row in self.hashes[1:]:
            h = scrypt.hash(row[0], row[1], int(row[2]), int(row[3]), int(row[4]))
            hhex = b2a_hex(h)
            self.assertEqual(hhex, bytes(row[5].encode("utf-8")))

    def test_hash_buflen_keyword(self):
        """Test hash takes keyword valid buflen"""
        h64 = scrypt.hash(self.input, self.salt, buflen=64)
        h128 = scrypt.hash(self.input, self.salt, buflen=128)
        self.assertEqual(len(h64), 64)
        self.assertEqual(len(h128), 128)

    def test_hash_n_positional(self):
        """Test hash accepts valid N in position 3"""
        h = scrypt.hash(self.input, self.salt, 256)
        self.assertEqual(len(h), 64)

    def test_hash_n_keyword(self):
        """Test hash takes keyword valid N"""
        h = scrypt.hash(N=256, password=self.input, salt=self.salt)
        self.assertEqual(len(h), 64)

    def test_hash_r_positional(self):
        """Test hash accepts valid r in position 4"""
        h = scrypt.hash(self.input, self.salt, 256, 16)
        self.assertEqual(len(h), 64)

    def test_hash_r_keyword(self):
        """Test hash takes keyword valid r"""
        h = scrypt.hash(r=16, password=self.input, salt=self.salt)
        self.assertEqual(len(h), 64)

    def test_hash_p_positional(self):
        """Test hash accepts valid p in position 5"""
        h = scrypt.hash(self.input, self.salt, 256, 8, 2)
        self.assertEqual(len(h), 64)

    def test_hash_p_keyword(self):
        """Test hash takes keyword valid p"""
        h = scrypt.hash(p=4, password=self.input, salt=self.salt)
        self.assertEqual(len(h), 64)

    def test_hash_raises_error_on_p_equals_zero(self):
        """Test hash raises scrypt error on illegal parameter value (p = 0)"""
        self.assertRaises(scrypt.error,
                          lambda: scrypt.hash(self.input, self.salt, p=0))

    def test_hash_raises_error_on_negative_p(self):
        """Test hash raises scrypt error on illegal parameter value (p < 0)"""
        self.assertRaises(scrypt.error,
                          lambda: scrypt.hash(self.input, self.salt, p=-1))

    def test_hash_raises_error_on_r_equals_zero(self):
        """Test hash raises scrypt error on illegal parameter value (r = 0)"""
        self.assertRaises(scrypt.error,
                          lambda: scrypt.hash(self.input, self.salt, r=0))

    def test_hash_raises_error_on_negative_r(self):
        """Test hash raises scrypt error on illegal parameter value (r < 1)"""
        self.assertRaises(scrypt.error,
                          lambda: scrypt.hash(self.input, self.salt, r=-1))

    def test_hash_raises_error_r_p_over_limit(self):
        """Test hash raises scrypt error when parameters r multiplied by p over limit 2**30"""
        self.assertRaises(scrypt.error,
                          lambda: scrypt.hash(self.input, self.salt, r=2, p=2 ** 29))

    def test_hash_raises_error_n_not_power_of_two(self):
        """Test hash raises scrypt error when parameter N is not a power of two {2, 4, 8, 16, etc}"""
        self.assertRaises(scrypt.error,
                          lambda: scrypt.hash(self.input, self.salt, N=3))

    def test_hash_raises_error_n_under_limit(self):
        """Test hash raises scrypt error when parameter N under limit of 1"""
        self.assertRaises(scrypt.error,
                          lambda: scrypt.hash(self.input, self.salt, N=1))
        self.assertRaises(scrypt.error,
                          lambda: scrypt.hash(self.input, self.salt, N=-1))


if __name__ == "__main__":
    testm.main()
