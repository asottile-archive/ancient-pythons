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

/* Operating system module implementation for MS-DOS */
/* Tested with Microsoft C 7.0 (as part of MSVC++ Pro 1.0) */

#include <dos.h>

#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <setjmp.h>
#include <sys/types.h>
#include <sys/stat.h>

#include <direct.h> /* chdir(), mkdir(), rmdir(), getcwd() */

#include "allobjects.h"
#include "modsupport.h"
#include "ceval.h"


/* Return a dictionary corresponding to the DOS environment table */

static object *
convertenviron()
{
	object *d;
	char **e;
	d = newdictobject();
	if (d == NULL)
		return NULL;
	if (environ == NULL)
		return d;
	/* XXX This part ignores errors */
	for (e = environ; *e != NULL; e++) {
		object *v;
		char *p = strchr(*e, '=');
		if (p == NULL)
			continue;
		v = newstringobject(p+1);
		if (v == NULL)
			continue;
		*p = '\0';
		(void) dictinsert(d, *e, v);
		*p = '=';
		DECREF(v);
	}
	return d;
}


static object *DosError; /* Exception dos.error */

/* Set a DOS-specific error from errno, and return NULL */

static object *
dos_error()
{
 	return err_errno(DosError);
}


/* DOS generic methods */

static object *
dos_1str(args, func)
	object *args;
	int (*func) FPROTO((const char *));
{
	char *path1;
	int res;
	if (!getargs(args, "s", &path1))
		return NULL;
	BGN_SAVE
	res = (*func)(path1);
	END_SAVE
	if (res < 0)
		return dos_error();
	INCREF(None);
	return None;
}

static object *
dos_2str(args, func)
	object *args;
	int (*func) FPROTO((const char *, const char *));
{
	char *path1, *path2;
	int res;
	if (!getargs(args, "(ss)", &path1, &path2))
		return NULL;
	BGN_SAVE
	res = (*func)(path1, path2);
	END_SAVE
	if (res < 0)
		return dos_error();
	INCREF(None);
	return None;
}

static object *
dos_strint(args, func)
	object *args;
	int (*func) FPROTO((const char *, int));
{
	char *path;
	int i;
	int res;
	if (!getargs(args, "(si)", &path, &i))
		return NULL;
	BGN_SAVE
	res = (*func)(path, i);
	END_SAVE
	if (res < 0)
		return dos_error();
	INCREF(None);
	return None;
}

static object *
dos_do_stat(self, args, statfunc)
	object *self;
	object *args;
	int (*statfunc) FPROTO((const char *, struct stat *));
{
	struct stat st;
	char *path;
	int res;
	if (!getargs(args, "s", &path))
		return NULL;
	BGN_SAVE
	res = (*statfunc)(path, &st);
	END_SAVE
	if (res != 0)
		return dos_error();
	return mkvalue("(llllllllll)",
		    (long)st.st_mode,
		    (long)st.st_ino,
		    (long)st.st_dev,
		    (long)st.st_nlink,
		    (long)st.st_uid,
		    (long)st.st_gid,
		    (long)st.st_size,
		    (long)st.st_atime,
		    (long)st.st_mtime,
		    (long)st.st_ctime);
}


/* DOS methods */

static object *
dos_chdir(self, args)
	object *self;
	object *args;
{
	return dos_1str(args, chdir);
}

static object *
dos_chmod(self, args)
	object *self;
	object *args;
{
	extern int chmod();
	return dos_strint(args, chmod);
}

static object *
dos_getcwd(self, args)
	object *self;
	object *args;
{
	char buf[1026];
	char *res;
	if (!getnoarg(args))
		return NULL;
	BGN_SAVE
	res = getcwd(buf, sizeof buf);
	END_SAVE
	if (res == NULL)
		return dos_error();
	return newstringobject(buf);
}

static object *
dos_listdir(self, args)
	object *self;
	object *args;
{
	char *name;
	int len;
	object *d, *v;
	struct find_t ep;
	int rv;
	char namebuf[256];

	if (!getargs(args, "s#", &name, &len))
		return NULL;
	if (len >= 250) {
		err_setstr(ValueError, "path too long");
		return NULL;
	}
	strcpy(namebuf, name);
	if (namebuf[len-1] != '/' && namebuf[len-1] != '\\')
		namebuf[len++] = '/';
	strcpy(namebuf + len, "*.*");

	if ((d = newlistobject(0)) == NULL)
		return NULL;

	if (_dos_findfirst(namebuf,
			_A_HIDDEN|_A_RDONLY|_A_SYSTEM|_A_SUBDIR, &ep) != 0)
		return dos_error();
	do {
		char *p;
		for (p = ep.name; *p != '\0'; p++)
			*p = tolower(*p);
		v = newstringobject(ep.name);
		if (v == NULL) {
			DECREF(d);
			d = NULL;
			break;
		}
		if (addlistitem(d, v) != 0) {
			DECREF(v);
			DECREF(d);
			d = NULL;
			break;
		}
		DECREF(v);
	} while (_dos_findnext(&ep) == 0);

	return d;
}

static object *
dos_mkdir(self, args)
	object *self;
	object *args;
{
	return dos_strint(args, mkdir);
}

static object *
dos_rename(self, args)
	object *self;
	object *args;
{
	return dos_2str(args, rename);
}

static object *
dos_rmdir(self, args)
	object *self;
	object *args;
{
	return dos_1str(args, rmdir);
}

static object *
dos_stat(self, args)
	object *self;
	object *args;
{
	return dos_do_stat(self, args, stat);
}

static object *
dos_system(self, args)
	object *self;
	object *args;
{
	char *command;
	long sts;
	if (!getargs(args, "s", &command))
		return NULL;
	BGN_SAVE
	sts = system(command);
	END_SAVE
	return newintobject(sts);
}

static object *
dos_unlink(self, args)
	object *self;
	object *args;
{
	return dos_1str(args, unlink);
}

static object *
dos_utime(self, args)
	object *self;
	object *args;
{
	char *path;
	int res;

#ifdef UTIME_STRUCT
	struct utimbuf buf;
#define ATIME buf.actime
#define MTIME buf.modtime
#define UTIME_ARG &buf

#else
	time_t buf[2];
#define ATIME buf[0]
#define MTIME buf[1]
#define UTIME_ARG buf
#endif

	if (!getargs(args, "(s(ll))", &path, &ATIME, &MTIME))
		return NULL;
	BGN_SAVE
	res = utime(path, UTIME_ARG);
	END_SAVE
	if (res < 0)
		return dos_error();
	INCREF(None);
	return None;
#undef UTIME_ARG
#undef ATIME
#undef MTIME
}

/* Functions acting on file descriptors */

static object *
dos_open(self, args)
	object *self;
	object *args;
{
	char *file;
	int flag;
	int mode = 0777;
	int fd;
	if (!getargs(args, "(si)", &file, &flag)) {
		err_clear();
		if (!getargs(args, "(sii)", &file, &flag, &mode))
			return NULL;
	}
	BGN_SAVE
	fd = open(file, flag, mode);
	END_SAVE
	if (fd < 0)
		return dos_error();
	return newintobject((long)fd);
}

static object *
dos_close(self, args)
	object *self;
	object *args;
{
	int fd, res;
	if (!getargs(args, "i", &fd))
		return NULL;
	BGN_SAVE
	res = close(fd);
	END_SAVE
	if (res < 0)
		return dos_error();
	INCREF(None);
	return None;
}

static object *
dos_dup(self, args)
	object *self;
	object *args;
{
	int fd;
	if (!getargs(args, "i", &fd))
		return NULL;
	BGN_SAVE
	fd = dup(fd);
	END_SAVE
	if (fd < 0)
		return dos_error();
	return newintobject((long)fd);
}

static object *
dos_dup2(self, args)
	object *self;
	object *args;
{
	int fd, fd2, res;
	if (!getargs(args, "(ii)", &fd, &fd2))
		return NULL;
	BGN_SAVE
	res = dup2(fd, fd2);
	END_SAVE
	if (res < 0)
		return dos_error();
	INCREF(None);
	return None;
}

static object *
dos_lseek(self, args)
	object *self;
	object *args;
{
	int fd, how;
	long pos, res;
	if (!getargs(args, "(ili)", &fd, &pos, &how))
		return NULL;
#ifdef SEEK_SET
	/* Turn 0, 1, 2 into SEEK_{SET,CUR,END} */
	switch (how) {
	case 0: how = SEEK_SET; break;
	case 1: how = SEEK_CUR; break;
	case 2: how = SEEK_END; break;
	}
#endif
	BGN_SAVE
	res = lseek(fd, pos, how);
	END_SAVE
	if (res < 0)
		return dos_error();
	return newintobject(res);
}

static object *
dos_read(self, args)
	object *self;
	object *args;
{
	int fd, size;
	object *buffer;
	if (!getargs(args, "(ii)", &fd, &size))
		return NULL;
	buffer = newsizedstringobject((char *)NULL, size);
	if (buffer == NULL)
		return NULL;
	BGN_SAVE
	size = read(fd, getstringvalue(buffer), size);
	END_SAVE
	if (size < 0) {
		DECREF(buffer);
		return dos_error();
	}
	resizestring(&buffer, size);
	return buffer;
}

static object *
dos_write(self, args)
	object *self;
	object *args;
{
	int fd, size;
	char *buffer;
	if (!getargs(args, "(is#)", &fd, &buffer, &size))
		return NULL;
	BGN_SAVE
	size = write(fd, buffer, size);
	END_SAVE
	if (size < 0)
		return dos_error();
	return newintobject((long)size);
}

static object *
dos_fstat(self, args)
	object *self;
	object *args;
{
	int fd;
	struct stat st;
	int res;
	if (!getargs(args, "i", &fd))
		return NULL;
	BGN_SAVE
	res = fstat(fd, &st);
	END_SAVE
	if (res != 0)
		return dos_error();
	return mkvalue("(llllllllll)",
		    (long)st.st_mode,
		    (long)st.st_ino,
		    (long)st.st_dev,
		    (long)st.st_nlink,
		    (long)st.st_uid,
		    (long)st.st_gid,
		    (long)st.st_size,
		    (long)st.st_atime,
		    (long)st.st_mtime,
		    (long)st.st_ctime);
}

static object *
dos_fdopen(self, args)
	object *self;
	object *args;
{
	extern int fclose PROTO((FILE *));
	int fd;
	char *mode;
	FILE *fp;
	if (!getargs(args, "(is)", &fd, &mode))
		return NULL;
	BGN_SAVE
	fp = fdopen(fd, mode);
	END_SAVE
	if (fp == NULL)
		return dos_error();
	return newopenfileobject(fp, "(fdopen)", mode, fclose);
}

static struct methodlist dos_methods[] = {
	{"chdir",	dos_chdir},
	{"chmod",	dos_chmod},
	{"getcwd",	dos_getcwd},
	{"listdir",	dos_listdir},
	{"mkdir",	dos_mkdir},
	{"rename",	dos_rename},
	{"rmdir",	dos_rmdir},
	{"stat",	dos_stat},
	{"system",	dos_system},
	{"unlink",	dos_unlink},
	{"utime",	dos_utime},
	{"open",	dos_open},
	{"close",	dos_close},
	{"dup",		dos_dup},
	{"dup2",	dos_dup2},
	{"lseek",	dos_lseek},
	{"read",	dos_read},
	{"write",	dos_write},
	{"fstat",	dos_fstat},
	{"fdopen",	dos_fdopen},
	{NULL,		NULL}		 /* Sentinel */
};


void
initdos()
{
	object *m, *d, *v;

	m = initmodule("dos", dos_methods);
	d = getmoduledict(m);

	/* Initialize dos.environ dictionary */
	v = convertenviron();
	if (v == NULL || dictinsert(d, "environ", v) != 0)
		fatal("can't define dos.environ");
	DECREF(v);

	/* Initialize dos.error exception */
	DosError = newstringobject("dos.error");
	if (DosError == NULL || dictinsert(d, "error", DosError) != 0)
		fatal("can't define dos.error");
}
