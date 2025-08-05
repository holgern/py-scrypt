#!/usr/bin/env python
import os
import sys
from ctypes import (
    POINTER,
    c_char_p,
    c_double,
    c_int,
    c_size_t,
    c_uint32,
    c_uint64,
    cdll,
    create_string_buffer,
    pointer,
)

if sys.version_info >= (3, 8) and sys.platform == "win32":
    lib_path = os.path.join(os.path.normpath(sys.prefix), "Library", "bin")
    build_dir = os.path.join(os.path.dirname(__file__), "../")
    if os.path.exists(lib_path):
        os.add_dll_directory(lib_path)
    if os.path.exists(build_dir):
        os.add_dll_directory(build_dir)
import importlib
import importlib.util
import os.path

# Fix for finding the _scrypt module
_scrypt_spec = importlib.util.find_spec("_scrypt")
if _scrypt_spec and hasattr(_scrypt_spec, "origin"):
    _scrypt = cdll.LoadLibrary(_scrypt_spec.origin)
else:
    # Fallback for Windows
    import os.path
    import sys

    if sys.platform == "win32":
        # Look for the DLL in common locations
        _scrypt_dll = "_scrypt.pyd"
        _path = os.path.abspath(os.path.dirname(__file__))
        _scrypt = cdll.LoadLibrary(os.path.join(_path, _scrypt_dll))

__version__ = "0.9.4"

# Declare C functions from libscrypt
_scryptenc_buf = _scrypt.exp_scryptenc_buf
_scryptenc_buf.argtypes = [
    c_char_p,  # const uint_t  *inbuf
    c_size_t,  # size_t         inbuflen
    c_char_p,  # uint8_t       *outbuf
    c_char_p,  # const uint8_t *passwd
    c_size_t,  # size_t         passwdlen
    c_size_t,  # size_t         maxmem
    c_double,  # double         maxmemfrac
    c_double,  # double         maxtime
    c_int,  # int            logN
    c_uint32,  # uint32_t       r
    c_uint32,  # uint32_t       p
    c_int,  # int            verbose
    c_int,  # int            force
]
_scryptenc_buf.restype = c_int

_scryptdec_buf = _scrypt.exp_scryptdec_buf
_scryptdec_buf.argtypes = [
    c_char_p,  # const uint8_t *inbuf
    c_size_t,  # size_t         inbuflen
    c_char_p,  # uint8_t       *outbuf
    POINTER(c_size_t),  # size_t        *outlen
    c_char_p,  # const uint8_t *passwd
    c_size_t,  # size_t         passwdlen
    c_size_t,  # size_t         maxmem
    c_double,  # double         maxmemfrac
    c_double,  # double         maxtime
    c_int,  # int            logN
    c_uint32,  # uint32_t       r
    c_uint32,  # uint32_t       p
    c_int,  # int            verbose
    c_int,  # int            force
]
_scryptdec_buf.restype = c_int

_crypto_scrypt = _scrypt.exp_crypto_scrypt
_crypto_scrypt.argtypes = [
    c_char_p,  # const uint8_t *passwd
    c_size_t,  # size_t         passwdlen
    c_char_p,  # const uint8_t *salt
    c_size_t,  # size_t         saltlen
    c_uint64,  # uint64_t       N
    c_uint32,  # uint32_t       r
    c_uint32,  # uint32_t       p
    c_char_p,  # uint8_t       *buf
    c_size_t,  # size_t         buflen
]
_crypto_scrypt.restype = c_int

# Define the pickparams C function interface
_pickparams = _scrypt.exp_pickparams
_pickparams.argtypes = [
    c_size_t,  # size_t maxmem
    c_double,  # double maxmemfrac
    c_double,  # double maxtime
    POINTER(c_int),  # int *logN
    POINTER(c_uint32),  # uint32_t *r
    POINTER(c_uint32),  # uint32_t *p
    c_int,  # int verbose
]
_pickparams.restype = c_int

# Define the checkparams C function interface
_checkparams = _scrypt.exp_checkparams
_checkparams.argtypes = [
    c_size_t,  # size_t maxmem
    c_double,  # double maxmemfrac
    c_double,  # double maxtime
    c_int,  # int logN
    c_uint32,  # uint32_t r
    c_uint32,  # uint32_t p
    c_int,  # int verbose
    c_int,  # int force
]
_checkparams.restype = c_int

ERROR_MESSAGES = [
    "success",
    "getrlimit or sysctl(hw.usermem) failed",
    "clock_getres or clock_gettime failed",
    "error computing derived key",
    "could not obtain cryptographically secure random bytes",
    "error in OpenSSL",
    "malloc failed",
    "data is not a valid scrypt-encrypted block",
    "unrecognized scrypt format",
    "decrypting file would take too much memory",
    "decrypting file would take too long",
    "password is incorrect",
    "error writing output file",
    "error reading input file",
    "error in explicit parameters",
    "error in explicit parameters (both SCRYPT_ETOOBIG and SCRYPT_ETOOSLOW)",
]

MAXMEM_DEFAULT = 0
MAXMEMFRAC_DEFAULT = 0.5
MAXTIME_DEFAULT = 300.0
MAXTIME_DEFAULT_ENC = 5.0


class error(Exception):
    def __init__(self, scrypt_code):
        if isinstance(scrypt_code, int):
            self._scrypt_code = scrypt_code
            super().__init__(ERROR_MESSAGES[scrypt_code])
        else:
            self._scrypt_code = -1
            super().__init__(scrypt_code)


def _ensure_bytes(data):
    """Convert data to bytes if it's a string, otherwise return as is.

    Args:
        data: String or bytes to convert

    Returns:
        bytes: The input converted to bytes if needed
    """
    if isinstance(data, str):
        return data.encode("utf-8")
    elif not isinstance(data, bytes):
        raise TypeError(f"Expected str or bytes, got {type(data).__name__}")

    return data


def encrypt(
    input,
    password,
    maxtime=MAXTIME_DEFAULT_ENC,
    maxmem=MAXMEM_DEFAULT,
    maxmemfrac=MAXMEMFRAC_DEFAULT,
    logN=0,
    r=0,
    p=0,
    force=False,
    verbose=False,
):
    """Encrypt data using a password.
    The resulting data will have len = len(input) + 128.

    - `input` and `password` can be both str and bytes. If they are str
      instances, they will be encoded with utf-8
    - The result will be a bytes instance
    - If logN, r, and p are all zero, optimal parameters will be chosen automatically
    - If logN, r, and p are provided,
      they must all be non-zero and will be used explicitly

    Args:
        input: Data to encrypt (bytes or str)
        password: Password for encryption (bytes or str)
        maxtime: Maximum time to spend in seconds
        maxmem: Maximum memory to use in bytes (0 for unlimited)
        maxmemfrac: Maximum fraction of available memory to use (0.0 to 1.0)
        logN: Log2 of the work factor (0 for automatic selection)
        r: Block size parameter (0 for automatic selection)
        p: Parallelization parameter (0 for automatic selection)
        force: If True, do not check whether encryption will exceed the estimated
               available memory or time
        verbose: If True, display parameter information

    Returns:
        bytes: Encrypted data

    Exceptions raised:
      - TypeError on invalid input
      - scrypt.error if encryption failed or parameters are invalid

    For more information on the `maxtime`, `maxmem`, and `maxmemfrac`
    parameters, see the scrypt documentation.
    """

    input = _ensure_bytes(input)
    password = _ensure_bytes(password)

    # All parameters must be 0 or all must be non-zero
    if not ((logN == 0 and r == 0 and p == 0) or (logN != 0 and r != 0 and p != 0)):
        raise error(
            "If providing explicit parameters, all of logN, r, and p must be non-zero"
        )

    # If parameters aren't provided, pick them automatically
    if logN == 0 and r == 0 and p == 0:
        logN, r, p = pickparams(maxmem, maxmemfrac, maxtime)

    outbuf = create_string_buffer(len(input) + 128)
    # verbose is set to zero
    result = _scryptenc_buf(
        input,
        len(input),
        outbuf,
        password,
        len(password),
        maxmem,
        maxmemfrac,
        maxtime,
        logN,
        r,
        p,
        1 if verbose else 0,  # verbose parameter
        1 if force else 0,  # force parameter
    )
    if result:
        raise error(result)

    return outbuf.raw


def decrypt(
    input,
    password,
    maxtime=MAXTIME_DEFAULT,
    maxmem=MAXMEM_DEFAULT,
    maxmemfrac=MAXMEMFRAC_DEFAULT,
    encoding="utf-8",
    verbose=False,
    force=False,
):
    """Decrypt data using a password.

    - `input` and `password` can be both str and bytes. If they are str
      instances, they will be encoded with utf-8. `input` *should*
      really be a bytes instance, since that's what `encrypt` returns.
    - The result will be a str instance decoded with `encoding`.
      If encoding=None, the result will be a bytes instance.

    Args:
        input: Encrypted data (bytes or str)
        password: Password for decryption (bytes or str)
        maxtime: Maximum time to spend in seconds
        maxmem: Maximum memory to use in bytes (0 for unlimited)
        maxmemfrac: Maximum fraction of available memory to use
        encoding: Encoding to use for output string (None for raw bytes)
        verbose: If True, display parameter information
        force: If True, do not check whether decryption will exceed the estimated
               available memory or time

    Returns:
        Decrypted data as str (if encoding is provided) or bytes (if encoding is None)

    Exceptions raised:
      - TypeError on invalid input
      - scrypt.error if decryption failed or if decoding with the specified
        encoding fails

    For more information on the `maxtime`, `maxmem`, and `maxmemfrac`
    parameters, see the scrypt documentation.
    """

    outbuf = create_string_buffer(len(input))
    outbuflen = pointer(c_size_t(0))

    input = _ensure_bytes(input)
    password = _ensure_bytes(password)
    # verbose and force are set to zero
    result = _scryptdec_buf(
        input,
        len(input),
        outbuf,
        outbuflen,
        password,
        len(password),
        maxmem,
        maxmemfrac,
        maxtime,
        0,
        0,
        0,
        1 if verbose else 0,  # verbose parameter
        1 if force else 0,  # force parameter
    )

    if result:
        raise error(result)

    out_bytes = outbuf.raw[: outbuflen.contents.value]

    if encoding is None:
        return out_bytes

    try:
        # More robust error handling for decoding
        return out_bytes.decode(encoding)
    except UnicodeDecodeError as e:
        raise error(f"Failed to decode using {encoding} encoding: {str(e)}") from e


def hash(password, salt, N=1 << 14, r=8, p=1, buflen=64):
    """Compute scrypt(password, salt, N, r, p, buflen).

    The parameters r, p, and buflen must satisfy r * p < 2^30 and
    buflen <= (2^32 - 1) * 32. The parameter N must be a power of 2
    greater than 1. N, r and p must all be positive.

    - `password` and `salt` can be both str and bytes. If they are str
    instances, they wil be encoded with utf-8.
    - The result will be a bytes instance

    Exceptions raised:
      - TypeError on invalid input
      - scrypt.error if scrypt failed
    """

    outbuf = create_string_buffer(buflen)

    password = _ensure_bytes(password)
    salt = _ensure_bytes(salt)

    if r * p >= (1 << 30) or N <= 1 or (N & (N - 1)) != 0 or p < 1 or r < 1:
        raise error(
            "hash parameters are wrong (r*p should be < 2**30, "
            "and N should be a power of two > 1)"
        )

    result = _crypto_scrypt(
        password, len(password), salt, len(salt), N, r, p, outbuf, buflen, 0
    )

    if result:
        raise error("could not compute hash")

    return outbuf.raw


def pickparams(
    maxmem=MAXMEM_DEFAULT,
    maxmemfrac=MAXMEMFRAC_DEFAULT,
    maxtime=MAXTIME_DEFAULT_ENC,
    verbose=0,
):
    """
    Pick the optimal scrypt parameters (logN, r, p) based on memory and CPU constraints.

    This function automatically determines the best parameters for scrypt encryption
    based on the available system resources. It balances security and performance
    by selecting parameters that will use as much memory and CPU time as allowed
    without exceeding the specified constraints.

    Args:
        maxmem: Maximum memory to use in bytes (0 for unlimited)
        maxmemfrac: Maximum fraction of available memory to use (0.0 to 1.0)
        maxtime: Maximum time to spend in seconds
        verbose: Whether to display parameter information (0 or 1)

    Returns:
        tuple: (logN, r, p) parameters for scrypt encryption
            - logN: The log2 of the work factor (N = 2^logN)
            - r: Block size parameter, fixed at 8 for compatibility
            - p: Parallelization parameter, adjusted based on CPU and memory

    Example:
        >>> from scrypt import pickparams
        >>> logN, r, p = pickparams(maxtime=2.0)
        >>> print(f"Optimal parameters: N=2^{logN} ({2**logN}), r={r}, p={p}")
    """
    # Create output parameters for the C function
    logN = c_int(0)
    r = c_uint32(0)
    p = c_uint32(0)

    # Call the C function
    result = _pickparams(
        maxmem, maxmemfrac, maxtime, pointer(logN), pointer(r), pointer(p), verbose
    )

    # Check for errors
    if result:
        raise error(result)

    return logN.value, r.value, p.value


def checkparams(
    logN,
    r,
    p,
    maxmem=MAXMEM_DEFAULT,
    maxmemfrac=MAXMEMFRAC_DEFAULT,
    maxtime=MAXTIME_DEFAULT_ENC,
    verbose=0,
    force=0,
):
    """
    Check if the provided scrypt parameters are valid and within resource limits.

    This function verifies that the scrypt parameters (logN, r, p) are valid and
    can be computed within the specified memory and CPU time constraints.

    Args:
        logN: Log2 of the work factor (N = 2^logN)
        r: Block size parameter
        p: Parallelization parameter
        maxmem: Maximum memory to use in bytes (0 for unlimited)
        maxmemfrac: Maximum fraction of available memory to use (0.0 to 1.0)
        maxtime: Maximum time to spend in seconds
        verbose: Whether to display parameter information (0 or 1)
        force: If 1, ignore resource limits

    Returns:
        0 on success, otherwise an error code

    Exceptions raised:
        - scrypt.error if parameters are invalid or would exceed resource limits
    """
    # Call the C function
    result = _checkparams(maxmem, maxmemfrac, maxtime, logN, r, p, verbose, force)

    # Check for errors
    if result:
        raise error(result)

    return 0


__all__ = ["error", "encrypt", "decrypt", "hash", "pickparams", "checkparams"]
