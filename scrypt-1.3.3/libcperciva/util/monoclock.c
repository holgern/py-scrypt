#include <errno.h>
#include <time.h>

#ifdef _MSC_VER
#include <Windows.h>
#include <sys/time.h> /* Use the Windows stub header */
#else
#include <sys/time.h>
#endif

#include "warnp.h"

#include "monoclock.h"

/* Determine which clock(s) to use. */
#ifndef POSIXFAIL_CLOCK_GETTIME
#ifdef CLOCK_MONOTONIC
#define USE_MONOTONIC
#endif
#ifndef POSIXFAIL_CLOCK_REALTIME
#define USE_REALTIME
#endif
#endif

/**
 * monoclock_get(tv):
 * Store the current time in ${tv}.  If CLOCK_MONOTONIC is available, use
 * that clock; if CLOCK_MONOTONIC is unavailable, use CLOCK_REALTIME (if
 * available) or gettimeofday(2).
 */
int
monoclock_get(struct timeval * tv)
{
#ifdef _MSC_VER
	/* 
	 * Windows doesn't have a monotonic clock, but we can use QueryPerformanceCounter
	 * which is high-resolution and generally monotonic.
	 */
	static LARGE_INTEGER freq = {0};
	LARGE_INTEGER count;
	
	/* Get the frequency on first call */
	if (freq.QuadPart == 0) {
		if (!QueryPerformanceFrequency(&freq)) {
			warnp("QueryPerformanceFrequency");
			goto err0;
		}
	}
	
	/* Get the current counter */
	if (!QueryPerformanceCounter(&count)) {
		warnp("QueryPerformanceCounter");
		goto err0;
	}
	
	/* Convert to timeval */
	tv->tv_sec = (long)(count.QuadPart / freq.QuadPart);
	tv->tv_usec = (long)((count.QuadPart % freq.QuadPart) * 1000000 / freq.QuadPart);
#else
#if defined(USE_MONOTONIC) || defined(USE_REALTIME)
	struct timespec tp;
#endif

#ifdef USE_MONOTONIC
	if (clock_gettime(CLOCK_MONOTONIC, &tp) == 0) {
		tv->tv_sec = tp.tv_sec;
		tv->tv_usec = (suseconds_t)(tp.tv_nsec / 1000);
	} else if ((errno != ENOSYS) && (errno != EINVAL)) {
		warnp("clock_gettime(CLOCK_MONOTONIC)");
		goto err0;
	} else
#endif
#ifdef USE_REALTIME
	if (clock_gettime(CLOCK_REALTIME, &tp) == 0) {
		tv->tv_sec = tp.tv_sec;
		tv->tv_usec = (suseconds_t)(tp.tv_nsec / 1000);
	} else {
		warnp("clock_gettime(CLOCK_REALTIME)");
		goto err0;
	}
#else
	if (gettimeofday(tv, NULL)) {
		warnp("gettimeofday");
		goto err0;
	}
#endif
#endif /* _MSC_VER */

	/* Success! */
	return (0);

err0:
	/* Failure! */
	return (-1);
}

/**
 * monoclock_get_cputime(tv):
 * Store in ${tv} the duration the process has been running if
 * CLOCK_PROCESS_CPUTIME_ID is available; fall back to monoclock_get()
 * otherwise.
 */
int
monoclock_get_cputime(struct timeval * tv)
{
#ifdef _MSC_VER
	FILETIME createTime, exitTime, kernelTime, userTime;
	ULARGE_INTEGER uUserTime;
	
	/* Get process times */
	if (!GetProcessTimes(GetCurrentProcess(), &createTime, &exitTime,
	    &kernelTime, &userTime)) {
		warnp("GetProcessTimes");
		goto err0;
	}
	
	/* Convert FILETIME to timeval (user time only) */
	uUserTime.LowPart = userTime.dwLowDateTime;
	uUserTime.HighPart = userTime.dwHighDateTime;
	
	/* Windows FILETIME is in 100-nanosecond intervals since Jan 1, 1601 */
	/* Convert to seconds and microseconds */
	tv->tv_sec = (long)(uUserTime.QuadPart / 10000000ULL);
	tv->tv_usec = (long)((uUserTime.QuadPart % 10000000ULL) / 10);
#else
	/* Use CLOCK_PROCESS_CPUTIME_ID if available. */
#ifdef CLOCK_PROCESS_CPUTIME_ID
	struct timespec tp;

	if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &tp) == 0) {
		tv->tv_sec = tp.tv_sec;
		tv->tv_usec = (suseconds_t)(tp.tv_nsec / 1000);
	} else if ((errno != ENOSYS) && (errno != EINVAL)) {
		warnp("clock_gettime(CLOCK_PROCESS_CPUTIME_ID)");
		goto err0;
	} else
#endif
	/* Fall back to monoclock_get(). */
	if (monoclock_get(tv))
		goto err0;
#endif /* _MSC_VER */

	/* Success! */
	return (0);

err0:
	/* Failure! */
	return (-1);
}

/**
 * monoclock_getres(resd):
 * Store an upper limit on timer granularity in ${resd}.  If CLOCK_MONOTONIC
 * is available, use that clock; if CLOCK_MONOTONIC is unavailable, use
 * CLOCK_REALTIME (if available) or gettimeofday(2).  For this value to be
 * meaningful, we assume that clock_getres(x) succeeds iff clock_gettime(x)
 * succeeds.
 */
int
monoclock_getres(double * resd)
{
#ifdef _MSC_VER
	static LARGE_INTEGER freq = {0};
	
	/* Get the frequency on first call */
	if (freq.QuadPart == 0) {
		if (!QueryPerformanceFrequency(&freq)) {
			warnp("QueryPerformanceFrequency");
			goto err0;
		}
	}
	
	/* Return resolution in seconds */
	*resd = 1.0 / (double)freq.QuadPart;
#else
#if defined(USE_MONOTONIC) || defined(USE_REALTIME)
	struct timespec res;
#endif

#ifdef USE_MONOTONIC
	if (clock_getres(CLOCK_MONOTONIC, &res) == 0) {
		/* Convert clock resolution to a double. */
		*resd = (double)res.tv_sec + (double)res.tv_nsec * 0.000000001;
	} else if ((errno != ENOSYS) && (errno != EINVAL)) {
		warnp("clock_getres(CLOCK_MONOTONIC)");
		goto err0;
	} else
#endif
#ifdef USE_REALTIME
	if (clock_getres(CLOCK_REALTIME, &res) == 0) {
		/* Convert clock resolution to a double. */
		*resd = (double)res.tv_sec + (double)res.tv_nsec * 0.000000001;
	} else {
		warnp("clock_getres(CLOCK_REALTIME)");
		goto err0;
	}
#else
	/*
	 * We'll be using gettimeofday().  There is no standard way of getting
	 * the resolution of this clock, but it seems safe to assume that it
	 * ticks at a minimum rate of CLOCKS_PER_SEC Hz (even though that is
	 * defined in relation to the measurement of processor time usage, not
	 * wallclock time); on non-broken systems we'll be relying on
	 * clock_gettime and clock_getres anyway.
	 */
	*resd = 1.0 / CLOCKS_PER_SEC;
#endif
#endif /* _MSC_VER */

	/* Success! */
	return (0);

#if !defined(_MSC_VER) && (defined(USE_MONOTONIC) || defined(USE_REALTIME))
err0:
	/* Failure! */
	return (-1);
#endif

#ifdef _MSC_VER
err0:
	/* Failure! */
	return (-1);
#endif
}
