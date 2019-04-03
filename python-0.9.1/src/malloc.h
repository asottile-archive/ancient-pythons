/***********************************************************
Copyright 1991 by Stichting Mathematisch Centrum, Amsterdam, The
Netherlands.

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

/* Lowest-level memory allocation interface */

#ifdef THINK_C
#define ANY void
#ifndef THINK_C_3_0
#define HAVE_STDLIB
#endif
#endif

#ifdef __STD_C__
#define ANY void
#define HAVE_STDLIB
#endif

#ifndef ANY
#define ANY char
#endif

#ifndef NULL
#define NULL 0
#endif

#define NEW(type, n) ( (type *) malloc((n) * sizeof(type)) )
#define RESIZE(p, type, n) \
       if ((p) == NULL) \
               (p) =  (type *) malloc((n) * sizeof(type)); \
       else \
               (p) = (type *) realloc((char *)(p), (n) * sizeof(type))
#define DEL(p) free((char *)p)
#define XDEL(p) if ((p) == NULL) ; else DEL(p)

#ifdef HAVE_STDLIB
#include <stdlib.h>
#else
extern ANY *malloc PROTO((unsigned int));
extern ANY *calloc PROTO((unsigned int, unsigned int));
extern ANY *realloc PROTO((ANY *, unsigned int));
extern void free PROTO((ANY *)); /* XXX sometimes int on Unix old systems */
#endif
