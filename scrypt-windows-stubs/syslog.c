#ifdef _MSC_VER

#include <stdarg.h>
#include <stdio.h>
#include <windows.h>
#include <syslog.h>

/* Implementation of syslog for Windows */
void 
syslog(int priority, const char *format, ...)
{
    va_list args;
    char buffer[4096]; /* Using a reasonable buffer size */
    
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    
    /* Log to Windows event log or just output to stderr */
    fprintf(stderr, "syslog: %s", buffer);
}

/* Implementation of closelog for Windows */
void 
closelog(void)
{
    /* Do nothing on Windows */
}

#endif /* _MSC_VER */