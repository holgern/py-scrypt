#!/usr/bin/env python
import os
import platform
import struct
import sys

from setuptools import Extension, setup

includes = []
libraries = []
library_dirs = []
extra_sources = []
CFLAGS = []


if sys.platform.startswith('linux'):
    define_macros = [
        ('HAVE_CLOCK_GETTIME', '1'),
        ('HAVE_LIBRT', '1'),
        ('HAVE_POSIX_MEMALIGN', '1'),
        ('HAVE_STRUCT_SYSINFO', '1'),
        ('HAVE_STRUCT_SYSINFO_MEM_UNIT', '1'),
        ('HAVE_STRUCT_SYSINFO_TOTALRAM', '1'),
        ('HAVE_SYSINFO', '1'),
        ('HAVE_SYS_SYSINFO_H', '1'),
        ('_FILE_OFFSET_BITS', '64'),
    ]
    libraries = ['crypto', 'rt']
    includes = ['/usr/local/include', '/usr/include']
    CFLAGS.append('-O2')
elif sys.platform.startswith('win32') and os.environ.get('MSYSTEM'):
    msys2_env = os.getenv('MSYSTEM')
    print(f'Building for MSYS2 {msys2_env!r} environment')
    if msys2_env not in ('UCRT64', 'MSYS'):
        print(
            'py-scrypt is untested with environment {!r}: you may experience problems'.format(
                msys2_env
            )
        )
    includes = {
        'UCRT64': [],
        'MSYS': ['/mingw64/include'],
        'MINGW32': ['/mingw32/include'],
        'MINGW64': ['/mingw64/include'],
        'CLANG32': ['/clang32/include'],
        'CLANG64': ['/clang64/include'],
        'CLANGARM64': ['/clangarm64/include'],
    }.get(msys2_env, [])
    define_macros = []
    libraries = ['libcrypto']
    CFLAGS.append('-O2')
elif sys.platform.startswith('win32'):
    define_macros = [('inline', '__inline')]

    extra_sources = ['scrypt-windows-stubs/gettimeofday.c']
    if struct.calcsize('P') == 8:
        if (
            os.path.isdir(r'c:\OpenSSL-v111-Win64')
            and sys.version_info[0] >= 3
            and sys.version_info[1] > 4
        ):
            openssl_dir = r'c:\OpenSSL-v111-Win64'
        elif os.path.isdir(r'c:\Program Files\OpenSSL-Win64'):
            openssl_dir = r'c:\Program Files\OpenSSL-Win64'
        elif os.path.isdir(r'c:\Program Files\OpenSSL'):
            openssl_dir = r'c:\Program Files\OpenSSL'
        else:
            openssl_dir = r'c:\OpenSSL-Win64'
        library_dirs = [openssl_dir + r'\lib']
        includes = [openssl_dir + r'\include', 'scrypt-windows-stubs/include']
    else:
        if os.path.isdir(r'c:\OpenSSL-v111-Win32'):
            openssl_dir = r'c:\OpenSSL-v111-Win32'
        elif os.path.isdir(r'c:\Program Files (x86)\OpenSSL-Win32'):
            openssl_dir = r'c:\Program Files (x86)\OpenSSL-Win32'
        elif os.path.isdir(r'c:\Program Files (x86)\OpenSSL'):
            openssl_dir = r'c:\Program Files (x86)\OpenSSL'
        else:
            openssl_dir = r'c:\OpenSSL-Win32'
        library_dirs = [openssl_dir + r'\lib']
        includes = [openssl_dir + r'\include', 'scrypt-windows-stubs/include']
    windows_link_legacy_openssl = os.environ.get(
        "SCRYPT_WINDOWS_LINK_LEGACY_OPENSSL", None
    )
    if windows_link_legacy_openssl is None:
        libraries = ['libcrypto_static']
    else:
        libraries = ['libeay32']
    libraries += ["advapi32", "gdi32", "user32", "ws2_32"]

elif sys.platform.startswith('darwin') and platform.mac_ver()[0] < '10.6':
    define_macros = [('HAVE_SYSCTL_HW_USERMEM', '1')]
    # disable for travis
    libraries = ['crypto']
elif sys.platform.startswith('darwin'):
    define_macros = [('HAVE_POSIX_MEMALIGN', '1'), ('HAVE_SYSCTL_HW_USERMEM', '1')]
    # disable for travis
    libraries = ['crypto']
else:
    define_macros = [('HAVE_POSIX_MEMALIGN', '1'), ('HAVE_SYSCTL_HW_USERMEM', '1')]
    libraries = ['crypto']

scrypt_module = Extension(
    '_scrypt',
    sources=[
        'src/scrypt.c',
        'scrypt-1.2.1/lib/crypto/crypto_scrypt_smix_sse2.c',
        'scrypt-1.2.1/lib/crypto/crypto_scrypt_smix.c',
        'scrypt-1.2.1/lib/crypto/crypto_scrypt.c',
        'scrypt-1.2.1/lib/scryptenc/scryptenc.c',
        'scrypt-1.2.1/lib/scryptenc/scryptenc_cpuperf.c',
        'scrypt-1.2.1/lib/util/memlimit.c',
        'scrypt-1.2.1/libcperciva/alg/sha256.c',
        'scrypt-1.2.1/libcperciva/crypto/crypto_aes_aesni.c',
        'scrypt-1.2.1/libcperciva/crypto/crypto_aes.c',
        'scrypt-1.2.1/libcperciva/crypto/crypto_aesctr.c',
        'scrypt-1.2.1/libcperciva/crypto/crypto_entropy.c',
        'scrypt-1.2.1/libcperciva/util/entropy.c',
        'scrypt-1.2.1/libcperciva/util/insecure_memzero.c',
        'scrypt-1.2.1/libcperciva/util/warnp.c',
        'scrypt-1.2.1/libcperciva/util/humansize.c',
        'scrypt-1.2.1/libcperciva/util/asprintf.c',
    ]
    + extra_sources,
    include_dirs=[
        'scrypt-1.2.1',
        'scrypt-1.2.1/lib',
        'scrypt-1.2.1/lib/scryptenc',
        'scrypt-1.2.1/lib/crypto',
        'scrypt-1.2.1/lib/util',
        'scrypt-1.2.1/libcperciva/cpusupport',
        'scrypt-1.2.1/libcperciva/alg',
        'scrypt-1.2.1/libcperciva/util',
        'scrypt-1.2.1/libcperciva/crypto',
    ]
    + includes,
    define_macros=[('HAVE_CONFIG_H', None)] + define_macros,
    extra_compile_args=CFLAGS,
    library_dirs=library_dirs,
    libraries=libraries,
)

setup(
    name='scrypt',
    version='0.8.27',
    description='Bindings for the scrypt key derivation function library',
    author='Magnus Hallin',
    author_email='mhallin@gmail.com',
    maintainer="Holger Nahrstaedt",
    maintainer_email="nahrstaedt@gmail.com",
    url='https://github.com/holgern/py-scrypt',
    packages=['scrypt', 'scrypt.tests'],
    package_data={'scrypt': ['tests/*.csv']},
    ext_modules=[scrypt_module],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries',
    ],
    license='2-clause BSD',
    long_description=open('README.rst').read(),
)
