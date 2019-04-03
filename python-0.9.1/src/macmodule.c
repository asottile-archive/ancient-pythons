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

/* Macintosh OS module implementation */

#include "allobjects.h"

#include "import.h"
#include "modsupport.h"

#include "sigtype.h"

#include "::unixemu:dir.h"
#include "::unixemu:stat.h"

static object *MacError; /* Exception */


static object *
mac_chdir(self, args)
       object *self;
       object *args;
{
       object *path;
       if (!getstrarg(args, &path))
               return NULL;
       if (chdir(getstringvalue(path)) != 0)
               return err_errno(MacError);
       INCREF(None);
       return None;
}


static object *
mac_getcwd(self, args)
       object *self;
       object *args;
{
       extern char *getwd();
       char buf[1025];
       if (!getnoarg(args))
               return NULL;
       strcpy(buf, "mac.getcwd() failed"); /* In case getwd() doesn't set a msg */
       if (getwd(buf) == NULL) {
               err_setstr(MacError, buf);
               return NULL;
       }
       return newstringobject(buf);
}


static object *
mac_listdir(self, args)
       object *self;
       object *args;
{
       object *name, *d, *v;
       DIR *dirp;
       struct direct *ep;
       if (!getstrarg(args, &name))
               return NULL;
       if ((dirp = opendir(getstringvalue(name))) == NULL)
               return err_errno(MacError);
       if ((d = newlistobject(0)) == NULL) {
               closedir(dirp);
               return NULL;
       }
       while ((ep = readdir(dirp)) != NULL) {
               v = newstringobject(ep->d_name);
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
       }
       closedir(dirp);
       return d;
}


static object *
mac_mkdir(self, args)
       object *self;
       object *args;
{
       object *path;
       int mode;
       if (!getstrintarg(args, &path, &mode))
               return NULL;
       if (mkdir(getstringvalue(path), mode) != 0)
               return err_errno(MacError);
       INCREF(None);
       return None;
}


static object *
mac_rename(self, args)
       object *self;
       object *args;
{
       object *src, *dst;
       if (!getstrstrarg(args, &src, &dst))
               return NULL;
       if (rename(getstringvalue(src), getstringvalue(dst)) != 0)
               return err_errno(MacError);
       INCREF(None);
       return None;
}


static object *
mac_rmdir(self, args)
       object *self;
       object *args;
{
       object *path;
       if (!getstrarg(args, &path))
               return NULL;
       if (rmdir(getstringvalue(path)) != 0)
               return err_errno(MacError);
       INCREF(None);
       return None;
}


static object *
mac_stat(self, args)
       object *self;
       object *args;
{
       struct stat st;
       object *path;
       object *v;
       if (!getstrarg(args, &path))
               return NULL;
       if (stat(getstringvalue(path), &st) != 0)
               return err_errno(MacError);
       v = newtupleobject(11);
       if (v == NULL)
               return NULL;
#define SET(i, val) settupleitem(v, i, newintobject((long)(val)))
#define XXX(i, val) SET(i, 0) /* For values my Mac stat doesn't support */
       SET(0, st.st_mode);
       XXX(1, st.st_ino);
       XXX(2, st.st_dev);
       XXX(3, st.st_nlink);
       XXX(4, st.st_uid);
       XXX(5, st.st_gid);
       SET(6, st.st_size);
       XXX(7, st.st_atime);
       SET(8, st.st_mtime);
       XXX(9, st.st_ctime);
       SET(10, st.st_rsize); /* Mac-specific: resource size */
#undef SET
       if (err_occurred()) {
               DECREF(v);
               return NULL;
       }
       return v;
}


static object *
mac_sync(self, args)
       object *self;
       object *args;
{
       if (!getnoarg(args))
               return NULL;
       sync();
       INCREF(None);
       return None;
}


static object *
mac_unlink(self, args)
       object *self;
       object *args;
{
       object *path;
       if (!getstrarg(args, &path))
               return NULL;
       if (unlink(getstringvalue(path)) != 0)
               return err_errno(MacError);
       INCREF(None);
       return None;
}


static struct methodlist mac_methods[] = {
       {"chdir",     mac_chdir},
       {"getcwd",    mac_getcwd},
       {"listdir",   mac_listdir},
       {"mkdir",     mac_mkdir},
       {"rename",    mac_rename},
       {"rmdir",     mac_rmdir},
       {"stat",      mac_stat},
       {"sync",      mac_sync},
       {"unlink",    mac_unlink},
       {NULL,          NULL}            /* Sentinel */
};


void
initmac()
{
       object *m, *d;

       m = initmodule("mac", mac_methods);
       d = getmoduledict(m);

       /* Initialize mac.error exception */
       MacError = newstringobject("mac.error");
       if (MacError == NULL || dictinsert(d, "error", MacError) != 0)
               fatal("can't define mac.error");
}
