=========================
 Python scrypt_ bindings
=========================

This is a set of Python_ bindings for the scrypt_ key derivation
function.

.. image:: https://img.shields.io/pypi/v/scrypt.svg
    :target: https://pypi.python.org/pypi/scrypt/
    :alt: Latest Version

.. image:: https://anaconda.org/conda-forge/scrypt/badges/version.svg
    :target: https://anaconda.org/conda-forge/scrypt

.. image:: https://anaconda.org/conda-forge/scrypt/badges/downloads.svg
    :target: https://anaconda.org/conda-forge/scrypt


Scrypt is useful when encrypting password as it is possible to specify
a *minimum* amount of time to use when encrypting and decrypting. If,
for example, a password takes 0.05 seconds to verify, a user won't
notice the slight delay when signing in, but doing a brute force
search of several billion passwords will take a considerable amount of
time. This is in contrast to more traditional hash functions such as
MD5 or the SHA family which can be implemented extremely fast on cheap
hardware.

Installation
============

Or you can install the latest release from PyPi::

    $ pip install scrypt

Users of the Anaconda_ Python distribution can directly obtain pre-built
Windows, Intel Linux or macOS / OSX binaries from the conda-forge channel.
This can be done via::

    $ conda install -c conda-forge scrypt


If you want py-scrypt for your Python 3 environment, just run the
above commands with your Python 3 interpreter. Py-scrypt supports both
Python 2 and 3.

From version 0.6.0 (not available on PyPi yet), py-scrypt supports
PyPy as well.

Build From Source
=================

For Debian and Ubuntu, please ensure that the following packages are installed:

.. code:: bash

    $ sudo apt-get install build-essential libssl-dev python-dev

For Fedora and RHEL-derivatives, please ensure that the following packages are installed:

.. code:: bash

    $ sudo yum install gcc openssl-devel python-devel

For OSX, please do the following::

    $ brew install openssl
    $ export CFLAGS="-I$(brew --prefix openssl)/include $CFLAGS"
    $ export LDFLAGS="-L$(brew --prefix openssl)/lib $LDFLAGS"

For OSX, you can also use the precompiled wheels. They are installed by::

    $ pip install scrypt

For Windows, please use the precompiled wheels. They are installed by::

    $ pip install scrypt

For Windows, when the package should be compiled, the development package from https://slproweb.com/products/Win32OpenSSL.html is needed.
It needs to be installed to `C:\OpenSSL-Win64` or `C:\Program Files\OpenSSL`. 

It is also possible to use the Chocolatey package manager to install OpenSSL:

```
choco install openssl
```

You can install py-scrypt from this repository if you want the latest
but possibly non-compiling version::

    $ git clone https://github.com/holgern/py-scrypt.git
    $ cd py-scrypt
    $ python setup.py build

    Become superuser (or use virtualenv):
    # python setup.py install

    Run tests after install:
    $ python setup.py test


Changelog
=========
0.9.0
-----
* Update to scrypt 1.3.3

0.8.29
------
* Fix build for OSX using openssl 3.0
* Build Wheel for Python 3.13
* switch to ruff

0.8.24
------
* Building of all wheels works with github actions

0.8.20
------
* Fix #8 by adding missing gettimeofday.c to MANIFEST.in

0.8.19
------
* Use RtlGenRandom instead of CryptGenRandom on windows (Thanks to https://github.com/veorq/cryptocoding/)
* Add check for c:\Program Files\OpenSSL-Win64 and c:\Program Files\OpenSSL-Win32

0.8.18
------
* add wheel for python 3.9

0.8.17
------

* add_dll_directory for python 3.8 on windows, as importlib.util.find_spec does not search all paths anymore

0.8.16
------

* Add additional test vector from RFC (thanks to @ChrisMacNaughton)

0.8.15
------

* Fix missing import


0.8.14
------

* fix imp deprecation warning


0.8.13
------

* improve build for conda forge

0.8.12
------

* Add SCRYPT_WINDOWS_LINK_LEGACY_OPENSSL environment variable, when set, openssl 1.0.2 is linked

0.8.11
------

* fix build for conda feedstock

0.8.10
------

* fix typo

0.8.9
-----

* use the static libcrypto_static for windows and openssl 1.1.1

0.8.8
-----

* setup.py for windows improved, works with openssl 1.0.2 and 1.1.1

0.8.7
-----

* setup.py for windows fixed

0.8.6
-----

* setup.py fixed, scrypt could not be imported in version 0.8.5

0.8.5
-----

* MANIFEST.in fixed
* scrypt.py moved into own scrypt directory with __init__.py
* openssl library path for osx wheel repaired

0.8.4
-----

* __version__ added to scrypt
* missing void in sha256.c fixed

0.8.3
-----

* scrypt updated to 1.2.1
* Wheels are created for python 3.6

Usage
=====

For encryption/decryption, the library exports two functions
``encrypt`` and ``decrypt``::

    >>> import scrypt
    >>> data = scrypt.encrypt('a secret message', 'password', maxtime=0.1) # This will take at least 0.1 seconds
    >>> data[:20]
    'scrypt\x00\r\x00\x00\x00\x08\x00\x00\x00\x01RX9H'
    >>> scrypt.decrypt(data, 'password', maxtime=0.1) # This will also take at least 0.1 seconds
    'a secret message'
    >>> scrypt.decrypt(data, 'password', maxtime=0.05) # scrypt won't be able to decrypt this data fast enough
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    scrypt.error: decrypting file would take too long
    >>> scrypt.decrypt(data, 'wrong password', maxtime=0.1) # scrypt will throw an exception if the password is incorrect
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    scrypt.error: password is incorrect

From these, one can make a simple password verifier using the following
functions::

    import os
    import scrypt

    def hash_password(password, maxtime=0.5, datalength=64):
        """Create a secure password hash using scrypt encryption.

        Args:
            password: The password to hash
            maxtime: Maximum time to spend hashing in seconds
            datalength: Length of the random data to encrypt

        Returns:
            bytes: An encrypted hash suitable for storage and later verification
        """
        return scrypt.encrypt(os.urandom(datalength), password, maxtime=maxtime)

    def verify_password(hashed_password, guessed_password, maxtime=0.5):
        """Verify a password against its hash with better error handling.

        Args:
            hashed_password: The stored password hash from hash_password()
            guessed_password: The password to verify
            maxtime: Maximum time to spend in verification

        Returns:
            tuple: (is_valid, status_code) where:
                - is_valid: True if password is correct, False otherwise
                - status_code: One of "correct", "wrong_password", "time_limit_exceeded",
                  "memory_limit_exceeded", or "error"

        Raises:
            scrypt.error: Only raised for resource limit errors, which you may want to
                        handle by retrying with higher limits or force=True
        """
        try:
            scrypt.decrypt(hashed_password, guessed_password, maxtime, encoding=None)
            return True, "correct"
        except scrypt.error as e:
            # Check the specific error message to differentiate between causes
            error_message = str(e)
            if error_message == "password is incorrect":
                # Wrong password was provided
                return False, "wrong_password"
            elif error_message == "decrypting file would take too long":
                # Time limit exceeded
                raise  # Re-raise so caller can handle appropriately
            elif error_message == "decrypting file would take too much memory":
                # Memory limit exceeded
                raise  # Re-raise so caller can handle appropriately
            else:
                # Some other error occurred (corrupted data, etc.)
                return False, "error"

    # Example usage:

    # Create a hash of a password
    stored_hash = hash_password("correct_password", maxtime=0.1)

    # Verify with correct password
    is_valid, status = verify_password(stored_hash, "correct_password", maxtime=0.1)
    if is_valid:
        print("Password is correct!")  # This will be printed

    # Verify with wrong password
    is_valid, status = verify_password(stored_hash, "wrong_password", maxtime=0.1)
    if not is_valid:
        if status == "wrong_password":
            print("Password is incorrect!")  # This will be printed

    # Verify with insufficient time
    try:
        # Set maxtime very low to trigger a time limit error
        is_valid, status = verify_password(stored_hash, "correct_password", maxtime=0.00001)
    except scrypt.error as e:
        if "would take too long" in str(e):
            print("Time limit exceeded, try with higher maxtime or force=True")

            # Retry with force=True
            result = scrypt.decrypt(stored_hash, "correct_password", maxtime=0.00001, force=True, encoding=None)
            print("Forced decryption successful!")

The `encrypt` function accepts several parameters to control its behavior::

    encrypt(input, password, maxtime=5.0, maxmem=0, maxmemfrac=0.5, logN=0, r=0, p=0, force=False, verbose=False)

Where:
    - `input`: Data to encrypt (bytes or str)
    - `password`: Password for encryption (bytes or str)
    - `maxtime`: Maximum time to spend in seconds
    - `maxmem`: Maximum memory to use in bytes (0 for unlimited)
    - `maxmemfrac`: Maximum fraction of available memory to use (0.0 to 1.0)
    - `logN`, `r`, `p`: Parameters controlling the scrypt key derivation function
      - If all three are zero (default), optimal parameters are chosen automatically
      - If provided, all three must be non-zero and will be used explicitly
    - `force`: If True, do not check whether encryption will exceed the estimated memory or time
    - `verbose`: If True, display parameter information

The `decrypt` function has a simpler interface::

    decrypt(input, password, maxtime=300.0, maxmem=0, maxmemfrac=0.5, encoding='utf-8', verbose=False, force=False)

Where:
    - `input`: Encrypted data (bytes or str)
    - `password`: Password for decryption (bytes or str)
    - `maxtime`: Maximum time to spend in seconds
    - `maxmem`: Maximum memory to use in bytes (0 for unlimited)
    - `maxmemfrac`: Maximum fraction of available memory to use
    - `encoding`: Encoding to use for output string (None for raw bytes)
    - `verbose`: If True, display parameter information
    - `force`: If True, do not check whether decryption will exceed the estimated memory or time


But, if you want output that is deterministic and constant in size,
you can use the ``hash`` function::

    >>> import scrypt
    >>> h1 = scrypt.hash('password', 'random salt')
    >>> len(h1)  # The hash will be 64 bytes by default, but is overridable.
    64
    >>> h1[:10]
    '\xfe\x87\xf3hS\tUo\xcd\xc8'
    >>> h2 = scrypt.hash('password', 'random salt')
    >>> h1 == h2 # The hash function is deterministic
    True

The `hash` function accepts the following parameters::

    hash(password, salt, N=1<<14, r=8, p=1, buflen=64)

Where:
    - `password`: The password to hash (bytes or str)
    - `salt`: Salt for the hash (bytes or str)
    - `N`: CPU/memory cost parameter (must be a power of 2)
    - `r`: Block size parameter
    - `p`: Parallelization parameter
    - `buflen`: Output buffer length

The parameters r, p, and buflen must satisfy r * p < 2^30 and
buflen <= (2^32 - 1) * 32. The parameter N must be a power of 2
greater than 1. N, r, and p must all be positive.

For advanced usage, the library also provides two utility functions:

- `pickparams(maxmem=0, maxmemfrac=0.5, maxtime=5.0, verbose=0)`:
  Automatically chooses optimal scrypt parameters based on system resources.
  Returns (logN, r, p) tuple.

- `checkparams(logN, r, p, maxmem=0, maxmemfrac=0.5, maxtime=5.0, verbose=0, force=0)`:
  Verifies that the provided parameters are valid and within resource limits.


Acknowledgements
================

Scrypt_ was created by Colin Percival and is licensed as 2-clause BSD.
Since scrypt does not normally build as a shared library, I have included
the source for the currently latest version of the library in this
repository. When a new version arrives, I will update these sources.

`Kelvin Wong`_ on Bitbucket provided changes to make the library
available on Mac OS X 10.6 and earlier, as well as changes to make the
library work more like the command-line version of scrypt by
default. Kelvin also contributed with the unit tests, lots of cross
platform testing and work on the ``hash`` function.

Burstaholic_ on Bitbucket provided the necessary changes to make
the library build on Windows.

The `python-appveyor-demo`_ repository for setting up automated Windows
builds for a multitude of Python versions.

License
=======

This library is licensed under the same license as scrypt; 2-clause BSD.

.. _scrypt: http://www.tarsnap.com/scrypt.html
.. _Python: http://python.org
.. _Burstaholic: https://bitbucket.org/Burstaholic
.. _Kelvin Wong: https://bitbucket.org/kelvinwong_ca
.. _python-appveyor-demo: https://github.com/ogrisel/python-appveyor-demo
.. _Anaconda: https://www.continuum.io
