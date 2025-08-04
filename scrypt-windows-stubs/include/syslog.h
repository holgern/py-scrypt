#ifndef _MY_SYSLOG_H_
#define _MY_SYSLOG_H_

#ifdef _MSC_VER

/* Define syslog constants for Windows */
#define LOG_EMERG       0       /* system is unusable */
#define LOG_ALERT       1       /* action must be taken immediately */
#define LOG_CRIT        2       /* critical conditions */
#define LOG_ERR         3       /* error conditions */
#define LOG_WARNING     4       /* warning conditions */
#define LOG_NOTICE      5       /* normal but significant condition */
#define LOG_INFO        6       /* informational */
#define LOG_DEBUG       7       /* debug-level messages */

/* Declare syslog functions - implementations are provided in syslog.c */
void syslog(int priority, const char *format, ...);
void closelog(void);

#endif /* _MSC_VER */

#endif /* _MY_SYSLOG_H_ */