/***********************************************************
Copyright 1991, 1992, 1993, 1994 by Stichting Mathematisch Centrum,
Amsterdam, The Netherlands.

                        All Rights Reserved

Permission to use, copy, modify, and distribute this software and its 
documentation for any purpose and without fee is hereby granted, 
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in 
supporting documentation, and that the names of Stichting Mathematisch
Centrum or CWI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior permission.

STICHTING MATHEMATISCH CENTRUM DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH CENTRUM BE LIABLE
FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

******************************************************************/

/* Time module */

#include "allobjects.h"
#include "modsupport.h"
#include "ceval.h"

#include <signal.h>
#include <setjmp.h>

#ifndef macintosh
#include <sys/types.h>
#endif

#ifdef QUICKWIN
#include <io.h>
#endif

#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif

#ifdef HAVE_SELECT
#include "myselect.h"
#else
#include "mytime.h"
#endif

#if HAVE_FTIME
#include <sys/timeb.h>
#endif

/* Forward declarations */
static void floatsleep PROTO((double));
static double floattime PROTO(());

static object *
time_time(self, args)
	object *self;
	object *args;
{
	double secs;
	if (!getnoarg(args))
		return NULL;
	secs = floattime();
	if (secs == 0.0) {
		err_errno(IOError);
		return NULL;
	}
	return newfloatobject(secs);
}

#ifdef HAVE_CLOCK

#ifndef CLOCKS_PER_SEC
#define CLOCKS_PER_SEC 1000000
#endif

static object *
time_clock(self, args)
	object *self;
	object *args;
{
	if (!getnoarg(args))
		return NULL;
	return newfloatobject(((double)clock()) / CLOCKS_PER_SEC);
}
#endif /* HAVE_CLOCK */

#ifdef SIGINT
static jmp_buf sleep_intr;

/* ARGSUSED */
static void
sleep_catcher(sig)
	int sig; /* Not used but required by interface */
{
	longjmp(sleep_intr, 1);
}
#endif /* SIGINT */

static object *
time_sleep(self, args)
	object *self;
	object *args;
{
	double secs;
#ifdef SIGINT
	/* We must set the signal handler *after* calling setjmp, to
	   avoid a race condition.  Unfortunately some compilers put
	   the sigsave variable in a register.  Sometimes auto is
	   enough, sometimes static is needed to avoid this (Microsoft
	   C 7.0). */
#ifdef WITH_THREAD
	auto
#else
	static
#endif
	       RETSIGTYPE (*sigsave)() = 0; /* Initialized to shut lint up */
#endif /* SIGINT */
	if (!getargs(args, "d", &secs))
		return NULL;
#ifdef SIGINT
	BGN_SAVE
	if (setjmp(sleep_intr)) {
		RET_SAVE
		signal(SIGINT, sigsave);
		err_set(KeyboardInterrupt);
		return NULL;
	}
	sigsave = signal(SIGINT, SIG_IGN);
	if (sigsave != (RETSIGTYPE (*)()) SIG_IGN)
		signal(SIGINT, sleep_catcher);
#endif
	floatsleep(secs);
#ifdef SIGINT
	END_SAVE
	signal(SIGINT, sigsave);
#endif
	INCREF(None);
	return None;
}

static object *
time_convert(when, function)
	time_t when;
	struct tm * (*function) PROTO((time_t *));
{
	struct tm *p = function(&when);
	return mkvalue("(iiiiiiiii)",
		       p->tm_year + 1900,
		       p->tm_mon + 1, /* Want January == 1 */
		       p->tm_mday,
		       p->tm_hour,
		       p->tm_min,
		       p->tm_sec,
		       (p->tm_wday + 6) % 7, /* Want Monday == 0 */
		       p->tm_yday + 1, /* Want January, 1 == 1 */
		       p->tm_isdst);
}

static object *
time_gmtime(self, args)
	object *self;
	object *args;
{
	double when;
	if (!getargs(args, "d", &when))
		return NULL;
	return time_convert((time_t)when, gmtime);
}

static object *
time_localtime(self, args)
	object *self;
	object *args;
{
	double when;
	if (!getargs(args, "d", &when))
		return NULL;
	return time_convert((time_t)when, localtime);
}

static int
gettmarg(args, p)
	object *args;
	struct tm *p;
{
	if (!getargs(args, "(iiiiiiiii)",
		     &p->tm_year,
		     &p->tm_mon,
		     &p->tm_mday,
		     &p->tm_hour,
		     &p->tm_min,
		     &p->tm_sec,
		     &p->tm_wday,
		     &p->tm_yday,
		     &p->tm_isdst))
		return 0;
	if (p->tm_year >= 1900)
		p->tm_year -= 1900;
	p->tm_mon--;
	p->tm_wday = (p->tm_wday + 1) % 7;
	p->tm_yday--;
	return 1;
}

static object *
time_asctime(self, args)
	object *self;
	object *args;
{
	struct tm buf;
	char *p;
	if (!gettmarg(args, &buf))
		return NULL;
	p = asctime(&buf);
	if (p[24] == '\n')
		p[24] = '\0';
	return newstringobject(p);
}

static object *
time_ctime(self, args)
	object *self;
	object *args;
{
	double dt;
	time_t tt;
	char *p;
	if (!getargs(args, "d", &dt))
		return NULL;
	tt = dt;
	p = ctime(&tt);
	if (p[24] == '\n')
		p[24] = '\0';
	return newstringobject(p);
}

static object *
time_mktime(self, args)
	object *self;
	object *args;
{
	struct tm buf;
	if (!gettmarg(args, &buf))
		return NULL;
	return newintobject((long)mktime(&buf));
}

static struct methodlist time_methods[] = {
	{"time",	time_time},
#ifdef HAVE_CLOCK
	{"clock",	time_clock},
#endif
	{"sleep",	time_sleep},
	{"gmtime",	time_gmtime},
	{"localtime",	time_localtime},
	{"asctime",	time_asctime},
	{"ctime",	time_ctime},
	{"mktime",	time_mktime},
	{NULL,		NULL}		/* sentinel */
};

void
inittime()
{
	object *m, *d;
	m = initmodule("time", time_methods);
	d = getmoduledict(m);
#ifdef HAVE_TZNAME
	tzset();
	dictinsert(d, "timezone", newintobject((long)timezone));
#ifdef HAVE_ALTZONE
	dictinsert(d, "altzone", newintobject((long)altzone));
#else
	dictinsert(d, "altzone", newintobject((long)timezone-3600));
#endif
	dictinsert(d, "daylight", newintobject((long)daylight));
	dictinsert(d, "tzname", mkvalue("(zz)", tzname[0], tzname[1]));
#else /* !HAVE_TZNAME */
#if HAVE_TM_ZONE
	{
#define YEAR ((time_t)((365 * 24 + 6) * 3600))
		time_t t;
		struct tm *p;
		long winterzone, summerzone;
		char wintername[10], summername[10];
		/* XXX This won't work on the southern hemisphere.
		   XXX Anybody got a better idea? */
		t = (time((time_t *)0) / YEAR) * YEAR;
		p = localtime(&t);
		winterzone = -p->tm_gmtoff;
		strncpy(wintername, p->tm_zone ? p->tm_zone : "   ", 9);
		wintername[9] = '\0';
		t += YEAR/2;
		p = localtime(&t);
		summerzone = -p->tm_gmtoff;
		strncpy(summername, p->tm_zone ? p->tm_zone : "   ", 9);
		summername[9] = '\0';
		dictinsert(d, "timezone", newintobject(winterzone));
		dictinsert(d, "altzone", newintobject(summerzone));
		dictinsert(d, "daylight",
			   newintobject((long)(winterzone != summerzone)));
		dictinsert(d, "tzname",
			   mkvalue("(zz)", wintername, summername));
	}
#endif /* HAVE_TM_ZONE */
#endif /* !HAVE_TZNAME */
}


/* Implement floattime() for various platforms */

static double
floattime()
{
	/* There are three ways to get the time:
	   (1) gettimeofday() -- resolution in microseconds
	   (2) ftime() -- resolution in milliseconds
	   (3) time() -- resolution in seconds
	   In all cases the return value is a float in seconds.
	   Since on some systems (e.g. SCO ODT 3.0) gettimeofday() may
	   fail, so we fall back on ftime() or time().
	   Note: clock resolution does not imply clock accuracy! */
#ifdef HAVE_GETTIMEOFDAY
    {
	struct timeval t;
	if (gettimeofday(&t, (struct timezone *)NULL) == 0)
		return (double)t.tv_sec + t.tv_usec*0.000001;
    }
#endif /* !HAVE_GETTIMEOFDAY */
    {
#ifdef HAVE_FTIME
	struct timeb t;
	ftime(&t);
	return (double)t.time + t.millitm*0.001;
#else /* !HAVE_FTIME */
	time_t secs;
	time(&secs);
	return (double)secs;
#endif /* !HAVE_FTIME */
    }
}


/* Implement floatsleep() for various platforms */


static void
floatsleep(secs)
	double secs;
{
#ifdef HAVE_SELECT
	struct timeval t;
	double frac;
	extern double fmod PROTO((double, double));
	extern double floor PROTO((double));
	frac = fmod(secs, 1.0);
	secs = floor(secs);
	t.tv_sec = (long)secs;
	t.tv_usec = (long)(frac*1000000.0);
	(void) select(0, (fd_set *)0, (fd_set *)0, (fd_set *)0, &t);
#else /* !HAVE_SELECT */
#ifdef macintosh
#define MacTicks	(* (long *)0x16A)
	long deadline;
	deadline = MacTicks + (long)(secs * 60.0);
	while (MacTicks < deadline) {
		if (intrcheck())
			sleep_catcher(SIGINT);
	}
#else /* !macintosh */
#ifdef MSDOS
	struct timeb t1, t2;
	double frac;
	extern double fmod PROTO((double, double));
	extern double floor PROTO((double));
	if (secs <= 0.0)
		return;
	frac = fmod(secs, 1.0);
	secs = floor(secs);
	ftime(&t1);
	t2.time = t1.time + (int)secs;
	t2.millitm = t1.millitm + (int)(frac*1000.0);
	while (t2.millitm >= 1000) {
		t2.time++;
		t2.millitm -= 1000;
	}
	for (;;) {
#ifdef QUICKWIN
		_wyield();
#endif
		ftime(&t1);
		if (t1.time > t2.time ||
		    t1.time == t2.time && t1.millitm >= t2.millitm)
			break;
	}
#else /* !MSDOS */
	sleep((int)secs);
#endif /* !MSDOS */
#endif /* !macintosh */
#endif /* !HAVE_SELECT */
}
