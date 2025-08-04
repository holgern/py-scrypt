#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>

#ifdef _MSC_VER
#include <windows.h>
#include <wincrypt.h>
#else
#include <fcntl.h>
#include <unistd.h>
#endif

#include "warnp.h"

#include "entropy.h"

/**
 * XXX Portability
 * XXX We obtain random bytes from the operating system by opening
 * XXX /dev/urandom and reading them from that device; this works on
 * XXX modern UNIX-like operating systems but not on systems like
 * XXX win32 where there is no concept of /dev/urandom.
 */

/**
 * Entropy reader state.  This structure holds OS-dependent state:
 * - On Unix: a file descriptor for /dev/urandom
 * - On Windows: a cryptographic provider handle
 */
struct entropy_read_cookie {
#ifdef _MSC_VER
	HCRYPTPROV hCryptProv;
#else
	int fd;
#endif
};

/**
 * entropy_read_init(void):
 * Initialize the ability to produce random bytes from the operating system,
 * and return a cookie.
 */
struct entropy_read_cookie *
entropy_read_init(void)
{
	struct entropy_read_cookie * er;

	/* Allocate cookie. */
	if ((er = malloc(sizeof(struct entropy_read_cookie))) == NULL) {
		warnp("malloc");
		goto err0;
	}

#ifdef _MSC_VER
	/* Acquire a cryptographic provider context handle. */
	if (!CryptAcquireContext(&er->hCryptProv, NULL, NULL, 
	                         PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
		warnp("CryptAcquireContext");
		goto err1;
	}
#else
	/* Open /dev/urandom. */
	if ((er->fd = open("/dev/urandom", O_RDONLY)) == -1) {
		warnp("open(/dev/urandom)");
		goto err1;
	}
#endif

	/* Success! */
	return (er);

err1:
	free(er);
err0:
	/* Failure! */
	return (NULL);
}

/**
 * entropy_read_fill(er, buf, buflen):
 * Fill the given buffer with random bytes provided by the operating system
 * using the resources in ${er}.
 */
int
entropy_read_fill(struct entropy_read_cookie * er, uint8_t * buf,
    size_t buflen)
{
	/* Sanity checks. */
	assert(er != NULL);
	assert(buflen <= SSIZE_MAX);

#ifdef _MSC_VER
	/* Use Windows CryptoAPI to generate random bytes */
	if (!CryptGenRandom(er->hCryptProv, (DWORD)buflen, buf)) {
		warnp("CryptGenRandom");
		goto err0;
	}
#else
	ssize_t lenread;

	/* Read bytes until we have filled the buffer. */
	while (buflen > 0) {
		if ((lenread = read(er->fd, buf, buflen)) == -1) {
			warnp("read(/dev/urandom)");
			goto err0;
		}

		/* The random device should never EOF. */
		if (lenread == 0) {
			warn0("EOF on /dev/urandom?");
			goto err0;
		}

		/* We've filled a portion of the buffer. */
		buf += (size_t)lenread;
		buflen -= (size_t)lenread;
	}
#endif

	/* Success! */
	return (0);

err0:
	/* Failure! */
	return (-1);
}

/**
 * entropy_read_done(er):
 * Release any resources used by ${er}.
 */
int
entropy_read_done(struct entropy_read_cookie * er)
{
	/* Sanity check. */
	assert(er != NULL);

#ifdef _MSC_VER
	/* Release the cryptographic provider context */
	if (!CryptReleaseContext(er->hCryptProv, 0)) {
		warnp("CryptReleaseContext");
		goto err1;
	}
#else
	/* Close the device. */
	while (close(er->fd) == -1) {
		if (errno != EINTR) {
			warnp("close(/dev/urandom)");
			goto err1;
		}
	}
#endif

	/* Clean up. */
	free(er);

	/* Success! */
	return (0);

err1:
	free(er);

	/* Failure! */
	return (-1);
}

/**
 * entropy_read(buf, buflen):
 * Fill the given buffer with random bytes provided by the operating system.
 */
int
entropy_read(uint8_t * buf, size_t buflen)
{
	struct entropy_read_cookie * er;

	/* Sanity-check the buffer size. */
	assert(buflen <= SSIZE_MAX);

	/* Open /dev/urandom. */
	if ((er = entropy_read_init()) == NULL) {
		warn0("entropy_read_init");
		goto err0;
	}

	/* Read bytes until we have filled the buffer. */
	if (entropy_read_fill(er, buf, buflen)) {
		warn0("entropy_read_fill");
		goto err1;
	}

	/* Close the device. */
	if (entropy_read_done(er)) {
		warn0("entropy_read_done");
		goto err0;
	}

	/* Success! */
	return (0);

err1:
	entropy_read_done(er);
err0:
	/* Failure! */
	return (-1);
}
