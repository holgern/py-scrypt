#ifndef _MY_TERMIOS_H_
#define _MY_TERMIOS_H_

#ifdef _MSC_VER
/* 
 * Stub header for Windows - this isn't fully implemented
 * but provides the minimal set of definitions to make the code compile.
 */
#include <windows.h>

/* Termios structure stub */
typedef unsigned long tcflag_t;
typedef unsigned char cc_t;
typedef unsigned long speed_t;

#define NCCS 32

struct termios {
    tcflag_t c_iflag;    /* input modes */
    tcflag_t c_oflag;    /* output modes */
    tcflag_t c_cflag;    /* control modes */
    tcflag_t c_lflag;    /* local modes */
    cc_t c_cc[NCCS];     /* control characters */
};

/* Flags */
#define ECHO    0x00000001
#define ECHONL  0x00000002

/* Mode values */
#define TCSANOW     0
#define TCSAFLUSH   1

/* Function stubs for Windows */
static inline int tcgetattr(int fd, struct termios *termios_p) { return -1; }
static inline int tcsetattr(int fd, int optional_actions, const struct termios *termios_p) { return -1; }

#endif /* _MSC_VER */

#endif /* _MY_TERMIOS_H_ */