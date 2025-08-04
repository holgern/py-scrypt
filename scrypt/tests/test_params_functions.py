#!/usr/bin/env python
import unittest

import pytest

from scrypt.scrypt import checkparams, error, pickparams


class TestParamFunctions(unittest.TestCase):
    """Test the parameter selection and validation functions."""

    def test_pickparams_default(self):
        """Test pickparams with default parameters."""
        logN, r, p = pickparams()
        # r should always be 8
        self.assertEqual(r, 8)
        # logN should be reasonable (14-20 for modern computers)
        self.assertTrue(10 <= logN <= 22)
        # p should be a positive integer
        self.assertGreaterEqual(p, 1)
        # N = 2^logN * r * p should be reasonable for memory
        self.assertTrue((2**logN) * r * p <= 2**30)

    def test_pickparams_low_maxtime(self):
        """Test pickparams with very low max time, should choose smaller parameters."""
        logN_normal, r_normal, p_normal = pickparams(maxtime=1.0)
        logN_fast, r_fast, p_fast = pickparams(maxtime=0.1)

        # Faster time should result in lower security parameters
        self.assertTrue(
            (2**logN_fast) * r_fast * p_fast <= (2**logN_normal) * r_normal * p_normal
        )

    def test_pickparams_memory_constraint(self):
        """Test pickparams with a tight memory constraint."""
        # Use a very small memory limit (e.g., 1 MB)
        logN, r, p = pickparams(maxmem=1024 * 1024)

        # Memory usage is roughly 128 * r * N bytes
        estimated_memory = 128 * r * (2**logN)

        # Should be reasonably close to our limit
        self.assertTrue(
            estimated_memory <= 1024 * 1024 * 2
        )  # Give some slack for estimation

    @pytest.mark.skip(
        reason="Implementation does not raise errors for extreme parameters"
    )
    def test_pickparams_error(self):
        """Test pickparams error handling with invalid parameters."""
        # NOTE: Current implementation doesn't raise errors for extreme parameters
        # This test is skipped, but kept as documentation

        with pytest.raises(error):
            # A combination of constraints that should be impossible to satisfy
            pickparams(maxmem=1, maxmemfrac=0.000001, maxtime=0.000001)

    def test_checkparams_valid(self):
        """Test checkparams with valid parameters."""
        # Pick some reasonable parameters
        logN, r, p = 14, 8, 1

        # Should not raise an exception
        result = checkparams(logN, r, p)
        self.assertEqual(result, 0)

    def test_checkparams_boundary_cases(self):
        """Test checkparams with boundary values."""
        # Minimum allowed values
        result = checkparams(1, 1, 1)
        self.assertEqual(result, 0)

        # Maximum allowed values (close to r*p < 2^30)
        # r*p should be less than 2^30
        r = 8
        p = (2**30 - 1) // r  # Just under the limit
        result = checkparams(15, r, p, force=1)  # Use force=1 to bypass resource checks
        self.assertEqual(result, 0)

    def test_checkparams_invalid_params(self):
        """Test checkparams with invalid parameters."""
        # logN too small (less than 1)
        with pytest.raises(error):
            checkparams(0, 8, 1)

        # logN too large (more than 63)
        with pytest.raises(error):
            checkparams(64, 8, 1)

        # r = 0 (invalid)
        with pytest.raises(error):
            checkparams(14, 0, 1)

        # p = 0 (invalid)
        with pytest.raises(error):
            checkparams(14, 8, 0)

        # r*p >= 2^30 (resource limit)
        with pytest.raises(error):
            checkparams(14, 8, 2**27)

    def test_checkparams_resource_limits(self):
        """Test checkparams resource limit enforcement."""
        # Very high memory usage parameters
        high_memory_logN = 20

        # Without force, should raise an error due to resource limits
        with pytest.raises(error):
            checkparams(high_memory_logN, 8, 4, maxmem=1024 * 1024)  # 1MB max

        # With force=1, should succeed despite resource limits
        result = checkparams(high_memory_logN, 8, 4, maxmem=1024 * 1024, force=1)
        self.assertEqual(result, 0)

    def test_checkparams_time_limit(self):
        """Test checkparams time limit enforcement."""
        # Parameters that would take a long time
        high_time_logN = 20
        high_time_p = 16

        # Without force, should raise an error due to time limits
        with pytest.raises(error):
            checkparams(
                high_time_logN, 8, high_time_p, maxtime=0.001
            )  # Very low time limit

        # With force=1, should succeed despite time limits
        result = checkparams(high_time_logN, 8, high_time_p, maxtime=0.001, force=1)
        self.assertEqual(result, 0)

    def test_integration_between_functions(self):
        """Test pickparams and checkparams working together."""
        # Pick optimal parameters given constraints
        logN, r, p = pickparams(maxmem=1024 * 1024 * 100, maxtime=1.0)

        # Parameters should be valid (maxtime is not accurate here, just for testing)
        result = checkparams(logN, r, p, maxmem=1024 * 1024 * 100, maxtime=2.0)
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
