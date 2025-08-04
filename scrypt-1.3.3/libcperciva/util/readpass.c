#include <stdio.h>
#include <string.h>

#ifdef _MSC_VER
#include <windows.h>
#include <io.h>
#include <conio.h>
#include <signal.h>  /* Use the Windows signal.h */
#include <signal_stubs.h> /* Additional signal definitions */
#define isatty _isatty
#define fileno _fileno
#include <termios.h> /* Use our stub termios.h */
#include <unistd.h>  /* Use our stub unistd.h */
#else
#include <signal.h>
#include <termios.h>
#include <unistd.h>
#endif

#include "insecure_memzero.h"
#include "warnp.h"

#include "readpass.h"

#define MAXPASSLEN 2048

#ifdef _MSC_VER
/* Windows doesn't have all these signals, use only the ones available */
static const int badsigs[] = {
	SIGINT, SIGTERM
};
#else
/* Signals we need to block. */
static const int badsigs[] = {
	SIGALRM, SIGHUP, SIGINT,
	SIGPIPE, SIGQUIT, SIGTERM,
	SIGTSTP, SIGTTIN, SIGTTOU
};
#endif
#define NSIGS sizeof(badsigs)/sizeof(badsigs[0])

/* Highest signal number we care about. */
#define MAX2(a, b) ((a) > (b) ? (a) : (b))
#define MAX4(a, b, c, d) MAX2(MAX2(a, b), MAX2(c, d))
#define MAX8(a, b, c, d, e, f, g, h) MAX2(MAX4(a, b, c, d), MAX4(e, f, g, h))

#ifdef _MSC_VER
/* Windows only has a subset of signals, simplify */
#define MAXBADSIG	MAX2(SIGINT, SIGTERM)
#else
#define MAXBADSIG	MAX2(SIGALRM, MAX8(SIGHUP, SIGINT, SIGPIPE, SIGQUIT, \
			    SIGTERM, SIGTSTP, SIGTTIN, SIGTTOU))
#endif

/* Has a signal of this type been received? */
static volatile sig_atomic_t gotsig[MAXBADSIG + 1];

/* Signal handler. */
static void
handle(int sig)
{

	gotsig[sig] = 1;
}

#ifdef _MSC_VER
/* Windows signal handling is simpler */
static void
resetsigs(void* savedsa)
{
	size_t i;
	
	/* If we intercepted a signal, re-issue it. */
	for (i = 0; i < NSIGS; i++) {
		if (gotsig[badsigs[i]])
			raise(badsigs[i]);
	}
}
#else
/* Restore old signals and re-issue intercepted signals. */
static void
resetsigs(struct sigaction savedsa[NSIGS])
{
	size_t i;

	/* Restore old signals. */
	for (i = 0; i < NSIGS; i++)
		sigaction(badsigs[i], &savedsa[i], NULL);

	/* If we intercepted a signal, re-issue it. */
	for (i = 0; i < NSIGS; i++) {
		if (gotsig[badsigs[i]])
			raise(badsigs[i]);
	}
}
#endif

/**
 * readpass(passwd, prompt, confirmprompt, devtty):
 * If ${devtty} is 0, read a password from stdin.  If ${devtty} is 1, read a
 * password from /dev/tty if possible; if not, read from stdin.  If ${devtty}
 * is 2, read a password from /dev/tty if possible; if not, exit with an error.
 * If reading from a tty (either /dev/tty or stdin), disable echo and prompt
 * the user by printing ${prompt} to stderr.  If ${confirmprompt} is non-NULL,
 * read a second password (prompting if a terminal is being used) and repeat
 * until the user enters the same password twice.  Return the password as a
 * malloced NUL-terminated string via ${passwd}.
 */
int
readpass(char ** passwd, const char * prompt,
    const char * confirmprompt, int devtty)
{
	FILE * readfrom;
	char passbuf[MAXPASSLEN];
	char confpassbuf[MAXPASSLEN];
#ifdef _MSC_VER
	HANDLE hStdin = INVALID_HANDLE_VALUE;
	DWORD oldMode = 0;
	void* savedSigHandlers = NULL; /* Windows doesn't need sigaction */
	size_t i;
	int usingtty;
#else
	struct sigaction sa, savedsa[NSIGS];
	struct termios term, term_old;
	size_t i;
	int usingtty;
#endif

	/* Where should we read the password from? */
	switch (devtty) {
	case 0:
		/* Read directly from stdin. */
		readfrom = stdin;
		break;
	case 1:
		/* Try to open /dev/tty; if that fails, read from stdin. */
		if ((readfrom = fopen("/dev/tty", "r")) == NULL)
			readfrom = stdin;
		break;
	case 2:
		/* Try to open /dev/tty; if that fails, bail. */
		if ((readfrom = fopen("/dev/tty", "r")) == NULL) {
			warnp("fopen(/dev/tty)");
			goto err1;
		}
		break;
	default:
		warn0("readpass does not support devtty=%d", devtty);
		goto err1;
	}

#ifdef _MSC_VER
	/* We have not received any signals yet. */
	for (i = 0; i <= MAXBADSIG; i++)
		gotsig[i] = 0;
		
	/* Windows signal handling is simpler - just set handlers */
	for (i = 0; i < NSIGS; i++) {
		signal(badsigs[i], handle);
	}
	
	/* If we're reading from a terminal, try to disable echo. */
	if ((usingtty = isatty(fileno(readfrom))) != 0) {
		/* Get the console handle and current mode */
		hStdin = GetStdHandle(STD_INPUT_HANDLE);
		if (hStdin == INVALID_HANDLE_VALUE) {
			warnp("Cannot get stdin handle");
			goto err2;
		}
		
		/* Save the old mode */
		if (!GetConsoleMode(hStdin, &oldMode)) {
			warnp("Cannot get console mode");
			goto err2;
		}
		
		/* Set the new mode to disable echo */
		if (!SetConsoleMode(hStdin, oldMode & (~ENABLE_ECHO_INPUT))) {
			warnp("Cannot set console mode");
			goto err2;
		}
	}
#else
	/* We have not received any signals yet. */
	for (i = 0; i <= MAXBADSIG; i++)
		gotsig[i] = 0;

	/*
	 * If we receive a signal while we're reading the password, we might
	 * end up with echo disabled; to prevent this, we catch the signals
	 * here, and we'll re-send them to ourselves later after we re-enable
	 * terminal echo.
	 */
	sa.sa_handler = handle;
	sa.sa_flags = 0;
	sigemptyset(&sa.sa_mask);
	for (i = 0; i < NSIGS; i++)
		sigaction(badsigs[i], &sa, &savedsa[i]);

	/* If we're reading from a terminal, try to disable echo. */
	if ((usingtty = isatty(fileno(readfrom))) != 0) {
		if (tcgetattr(fileno(readfrom), &term_old)) {
			warnp("Cannot read terminal settings");
			goto err2;
		}
		memcpy(&term, &term_old, sizeof(struct termios));
		term.c_lflag = (term.c_lflag & ~((tcflag_t)ECHO)) | ECHONL;
		if (tcsetattr(fileno(readfrom), TCSANOW, &term)) {
			warnp("Cannot set terminal settings");
			goto err2;
		}
	}
#endif

retry:
	/* If we have a terminal, prompt the user to enter the password. */
	if (usingtty)
		fprintf(stderr, "%s: ", prompt);

#ifdef _MSC_VER
	/* Read the password using Windows-specific methods if using console */
	if (usingtty && readfrom == stdin) {
		size_t pos = 0;
		int ch;
		
		/* Read characters one at a time */
		while (pos < MAXPASSLEN - 1) {
			ch = _getch();
			if (ch == '\r' || ch == '\n') {
				break;
			} else if (ch == '\b') {
				/* Handle backspace */
				if (pos > 0)
					pos--;
			} else {
				passbuf[pos++] = (char)ch;
			}
		}
		passbuf[pos] = '\0';
		/* Add a newline since we're suppressing echo */
		fprintf(stderr, "\n");
	} else {
		/* Use standard method for files */
		if (fgets(passbuf, MAXPASSLEN, readfrom) == NULL) {
			if (feof(readfrom))
				warn0("EOF reading password");
			else
				warnp("Cannot read password");
			goto err3;
		}
	}
#else
	/* Read the password. */
	if (fgets(passbuf, MAXPASSLEN, readfrom) == NULL) {
		if (feof(readfrom))
			warn0("EOF reading password");
		else
			warnp("Cannot read password");
		goto err3;
	}
#endif

	/* Confirm the password if necessary. */
	if (confirmprompt != NULL) {
		if (usingtty)
			fprintf(stderr, "%s: ", confirmprompt);
#ifdef _MSC_VER
		/* Read confirmation password using Windows-specific methods if using console */
		if (usingtty && readfrom == stdin) {
			size_t pos = 0;
			int ch;
			
			/* Read characters one at a time */
			while (pos < MAXPASSLEN - 1) {
				ch = _getch();
				if (ch == '\r' || ch == '\n') {
					break;
				} else if (ch == '\b') {
					/* Handle backspace */
					if (pos > 0)
						pos--;
				} else {
					confpassbuf[pos++] = (char)ch;
				}
			}
			confpassbuf[pos] = '\0';
			/* Add a newline since we're suppressing echo */
			fprintf(stderr, "\n");
		} else {
			/* Use standard method for files */
			if (fgets(confpassbuf, MAXPASSLEN, readfrom) == NULL) {
				if (feof(readfrom))
					warn0("EOF reading password");
				else
					warnp("Cannot read password");
				goto err3;
			}
		}
#else
		if (fgets(confpassbuf, MAXPASSLEN, readfrom) == NULL) {
			if (feof(readfrom))
				warn0("EOF reading password");
			else
				warnp("Cannot read password");
			goto err3;
		}
#endif
		if (strcmp(passbuf, confpassbuf)) {
			fprintf(stderr,
			    "Passwords mismatch, please try again\n");
			goto retry;
		}
	}

	/* Terminate the string at the first "\r" or "\n" (if any). */
	passbuf[strcspn(passbuf, "\r\n")] = '\0';

#ifdef _MSC_VER
	/* If we changed terminal settings, reset them. */
	if (usingtty && hStdin != INVALID_HANDLE_VALUE)
		SetConsoleMode(hStdin, oldMode);
		
	/* Restore default signal handlers */
	for (i = 0; i < NSIGS; i++) {
		signal(badsigs[i], SIG_DFL);
	}
	
	/* Re-issue any signals we caught */
	resetsigs(NULL);
#else
	/* If we changed terminal settings, reset them. */
	if (usingtty)
		tcsetattr(fileno(readfrom), TCSANOW, &term_old);

	/* Restore old signals and re-issue intercepted signals. */
	resetsigs(savedsa);
#endif

	/* Close /dev/tty if we opened it. */
	if ((readfrom != stdin) && fclose(readfrom))
		warnp("fclose");

	/* Copy the password out. */
	if ((*passwd = strdup(passbuf)) == NULL) {
		warnp("Cannot allocate memory");
		goto err1;
	}

	/*
	 * Zero any stored passwords.  This is not guaranteed to work, since a
	 * "sufficiently intelligent" compiler can optimize these out due to
	 * the values not being accessed again; and even if we outwitted the
	 * compiler, all we can do is ensure that *a* buffer is zeroed but
	 * not that it is the only buffer containing the data in question.
	 * Unfortunately the C standard does not provide any way to mark data
	 * as "sensitive" in order to prevent extra copies being sprinkled
	 * around the implementation address space.
	 */
	insecure_memzero(passbuf, MAXPASSLEN);
	insecure_memzero(confpassbuf, MAXPASSLEN);

	/* Success! */
	return (0);

err3:
#ifdef _MSC_VER
	/* Reset terminal settings if necessary. */
	if (usingtty && hStdin != INVALID_HANDLE_VALUE)
		SetConsoleMode(hStdin, oldMode);
#else
	/* Reset terminal settings if necessary. */
	if (usingtty)
		tcsetattr(fileno(readfrom), TCSAFLUSH, &term_old);
#endif
err2:
	/* Close /dev/tty if we opened it. */
	if ((readfrom != stdin) && fclose(readfrom))
		warnp("fclose");

#ifdef _MSC_VER
	/* Restore default signal handlers */
	for (i = 0; i < NSIGS; i++) {
		signal(badsigs[i], SIG_DFL);
	}
	
	/* Re-issue any signals we caught */
	resetsigs(NULL);
#else
	/* Restore old signals and re-issue intercepted signals. */
	resetsigs(savedsa);
#endif
err1:
	/* Zero any stored passwords. */
	insecure_memzero(passbuf, MAXPASSLEN);
	insecure_memzero(confpassbuf, MAXPASSLEN);

	/* Failure! */
	return (-1);
}
