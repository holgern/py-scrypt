#ifndef _MY_SIGNAL_STUBS_H
#define _MY_SIGNAL_STUBS_H

#ifdef _MSC_VER

/* 
 * Define missing signal constants for Windows
 * These aren't used functionally but are included to make the code compile
 */
#ifndef SIGALRM
#define SIGALRM 14
#endif

#ifndef SIGHUP
#define SIGHUP 1
#endif

#ifndef SIGPIPE
#define SIGPIPE 13
#endif

#ifndef SIGQUIT
#define SIGQUIT 3
#endif

#ifndef SIGTSTP
#define SIGTSTP 18
#endif

#ifndef SIGTTIN
#define SIGTTIN 21
#endif

#ifndef SIGTTOU
#define SIGTTOU 22
#endif

/* Define sigaction struct for Windows */
struct sigaction {
    void (*sa_handler)(int);
    void (*sa_sigaction)(int, void*, void*);
    int sa_flags;
    void* sa_mask;
};

/* Define empty function stubs */
#define sigemptyset(set) (0)
#define sigaction(sig, act, oact) (0)

#endif /* _MSC_VER */

#endif /* _MY_SIGNAL_STUBS_H */