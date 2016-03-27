#ifndef Py_MYTIME_H
#define Py_MYTIME_H
#ifdef __cplusplus
extern "C" {
#endif

/* Include file instead of <time.h> and/or <sys/time.h> */

#ifdef TIME_WITH_SYS_TIME
#include <sys/time.h>
#include <time.h>
#else /* !TIME_WITH_SYS_TIME */
#ifdef HAVE_SYS_TIME_H
#include <sys/time.h>
#else /* !HAVE_SYS_TIME_H */
#include <time.h>
#endif /* !HAVE_SYS_TIME_H */
#endif /* !TIME_WITH_SYS_TIME */

#ifdef __cplusplus
}
#endif
#endif /* !Py_MYTIME_H */
