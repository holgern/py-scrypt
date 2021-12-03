#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <unistd.h>

#include "warnp.h"

#include "entropy.h"

#ifdef _WIN32
#include <windows.h>
#include <Wincrypt.h>
#define RtlGenRandom SystemFunction036
BOOLEAN NTAPI RtlGenRandom(PVOID RandomBuffer, ULONG RandomBufferLength);
#endif

/**
 * XXX Portability
 * XXX We obtain random bytes from the operating system by opening
 * XXX /dev/urandom and reading them from that device; this works on
 * XXX modern UNIX-like operating systems but not on systems like
 * XXX win32 where there is no concept of /dev/urandom.
 */

/**
 * entropy_read(buf, buflen):
 * Fill the given buffer with random bytes provided by the operating system.
 */
int
entropy_read(uint8_t * buf, size_t buflen)
{
	int fd;
	ssize_t lenread;

#ifndef _WIN32
	/* Sanity-check the buffer size. */
	if (buflen > SSIZE_MAX) {
		warn0("Programmer error: "
		    "Trying to read insane amount of random data: %zu",
		    buflen);
		goto err0;
	}

	/* Open /dev/urandom. */
	if ((fd = open("/dev/urandom", O_RDONLY)) == -1) {
		warnp("open(/dev/urandom)");
		goto err0;
	}

	/* Read bytes until we have filled the buffer. */
	while (buflen > 0) {
		if ((lenread = read(fd, buf, buflen)) == -1) {
			warnp("read(/dev/urandom)");
			goto err1;
		}

		/* The random device should never EOF. */
		if (lenread == 0) {
			warn0("EOF on /dev/urandom?");
			goto err1;
		}

		/* We've filled a portion of the buffer. */
		buf += (size_t)lenread;
		buflen -= (size_t)lenread;
	}

	/* Close the device. */
	while (close(fd) == -1) {
		if (errno != EINTR) {
			warnp("close(/dev/urandom)");
			goto err0;
		}
	}

	/* Success! */
	return (0);

err1:
	close(fd);
err0:
	/* Failure! */
	return (-1);

#else // _WIN32

    if(FALSE == RtlGenRandom(buf, buflen))
    {
        return (-1);
    }
    else{
		buf += buflen;
		return(0);
	}

#endif // _WIN32
}
