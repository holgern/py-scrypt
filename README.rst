Python scrypt_ bindings
========================

.. contents::

This github is  a clone of https://bitbucket.org/mhallin/py-scrypt. Please add issues and Pull-requests there.

This is a set of Python_ bindings for the scrypt_ key derivation
function.

Scrypt is useful when encrypting password as it is possible to specify
a *minimum* amount of time to use when encrypting and decrypting. If,
for example, a password takes 0.05 seconds to verify, a user won't
notice the slight delay when signing in, but doing a brute force
search of several billion passwords will take a considerable amount of
time. This is in contrast to more traditional hash functions such as
MD5 or the SHA family which can be implemented extremely fast on cheap
hardware.

Installation
------------

You can install py-scrypt from this repository if you want the latest
but possibly non-compiling version::

    $ git clone https://github.com/holgern/py-scrypt
    $ cd py-scrypt
    $ python setup.py build

    Become superuser (or use virtualenv):
    # python setup.py install

    Run tests after install:
    $ python setup.py test

Or you can install the latest release from PyPi::

    $ pip install scrypt

If you want py-scrypt for your Python 3 environment, just run the
above commands with your Python 3 interpreter. Py-scrypt supports both
Python 2 and 3.

From version 0.6.0 (not available on PyPi yet), py-scrypt supports
PyPy as well.

Usage
-----

Fore encryption/decryption, the library exports two functions
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

    def hash_password(password, maxtime=0.5, datalength=64):
        return scrypt.encrypt(os.urandom(datalength), password, maxtime=maxtime)

    def verify_password(hashed_password, guessed_password, maxtime=0.5):
        try:
            scrypt.decrypt(hashed_password, guessed_password, maxtime)
            return True
        except scrypt.error:
            return False


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


Acknowledgements
----------------
`scrypt-python`_ was created by Magnus Hallin and is licensed as 2-clause BSD.

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
-------

This library is licensed under the same license as scrypt; 2-clause BSD.

Badges
------
.. image:: https://travis-ci.org/holgern/py-scrypt.svg?branch=master
    :target: https://travis-ci.org/holgern/py-scrypt

.. image:: https://ci.appveyor.com/api/projects/status/h644bjbdawke9vf2?svg=true
    :target: https://ci.appveyor.com/project/HolgerNahrstaedt/py-scrypt-7uot6

.. _scrypt-python: https://bitbucket.org/mhallin/py-scrypt/
.. _scrypt: http://www.tarsnap.com/scrypt.html
.. _Python: http://python.org
.. _Burstaholic: https://bitbucket.org/Burstaholic
.. _Kelvin Wong: https://bitbucket.org/kelvinwong_ca
.. _python-appveyor-demo: https://github.com/ogrisel/python-appveyor-demo
