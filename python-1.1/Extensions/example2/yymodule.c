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

/* yy module */

#include "allobjects.h"
#include "modsupport.h"


/* Function of two integers returning integer */

static object *
yy_foo(self, args)
	object *self; /* Not used */
	object *args;
{
	long i, j;
	long res;
	if (!getargs(args, "(ll)", &i, &j))
		return NULL;
	res = i+j; /* XXX Do something here */
	return newintobject(res);
}


/* Function of no arguments returning None */

static object *
yy_bar(self, args)
	object *self; /* Not used */
	object *args;
{
	int i, j;
	if (!getnoarg(args))
		return NULL;
	/* XXX Do something here */
	INCREF(None);
	return None;
}


/* List of functions defined in the module */

static struct methodlist yy_methods[] = {
	{"foo",		yy_foo},
	{"bar",		yy_bar},
	{NULL,		NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called inityy) */

void
inityy()
{
	object *m, *d, *x;

	/* Create the module and add the functions */
	m = initmodule("yy", yy_methods);

	/* Add some symbolic constants to the module */
	d = getmoduledict(m);
	x = newstringobject("yy.error");
	dictinsert(d, "error", x);
	x = newintobject(42L);
	dictinsert(d, "magic", x);

	/* Check for errors */
	if (err_occurred())
		fatal("can't initialize module yy");
}
