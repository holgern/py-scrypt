/*-
 * Copyright 2010 Magnus Hallin
 *           2018 Holger Nahrstaedt
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

#include <Python.h>

#include "scryptenc.h"
#include "crypto_scrypt.h"

#if !defined(DL_EXPORT)

#if defined(HAVE_DECLSPEC_DLL)
#define DL_EXPORT(type) __declspec(dllexport) type
#else
#define DL_EXPORT(type) type
#endif

#endif


/* Exported trampolines */
DL_EXPORT(int) exp_scryptenc_buf(const uint8_t *inbuf, size_t inbuflen,
                                 uint8_t *outbuf,
                                 const uint8_t *passwd, size_t passwdlen,
                                 size_t maxmem, double maxmemfrac, double maxtime, int verbose) {
    return scryptenc_buf(inbuf, inbuflen, outbuf, passwd, passwdlen,
                         maxmem, maxmemfrac, maxtime, verbose);
}

DL_EXPORT(int) exp_scryptdec_buf(const uint8_t *inbuf, size_t inbuflen,
                                 uint8_t *outbuf, size_t *outbuflen,
                                 const uint8_t *passwd, size_t passwdlen,
                                 size_t maxmem, double maxmemfrac, double maxtime, int verbose, int force) {
    return scryptdec_buf(inbuf, inbuflen, outbuf, outbuflen, passwd, passwdlen,
                         maxmem, maxmemfrac, maxtime, verbose, force);
}

DL_EXPORT(int) exp_crypto_scrypt(const uint8_t *passwd, size_t passwdlen,
                                 const uint8_t *salt, size_t saltlen,
                                 uint64_t N, uint32_t r, uint32_t p,
                                 uint8_t *buf, size_t buflen) {
    return crypto_scrypt(passwd, passwdlen, salt, saltlen,
                         N, r, p, buf, buflen);
}

/*
  We need a stub init_scrypt function so the module will link as a proper module.
*/

static PyMethodDef scrypt_methods[] = {
    {NULL, NULL, 0, NULL},
};

#if PY_MAJOR_VERSION == 2

PyMODINIT_FUNC init_scrypt(void) {
    Py_InitModule("_scrypt", scrypt_methods);
}

#endif

#if PY_MAJOR_VERSION == 3

static struct PyModuleDef scrypt_module = {
    PyModuleDef_HEAD_INIT,
    "_scrypt",
    NULL,
    -1,
    scrypt_methods
};

PyMODINIT_FUNC PyInit__scrypt(void) {
    return PyModule_Create(&scrypt_module);
}

#endif
