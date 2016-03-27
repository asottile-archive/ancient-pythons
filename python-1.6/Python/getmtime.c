/* Subroutine to get the last modification time of a file */

/* (A separate file because this may be OS dependent) */

#include "config.h"

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>

long
PyOS_GetLastModificationTime(path, fp)
	char *path;
	FILE *fp;
{
	struct stat st;
	if (fstat(fileno(fp), &st) != 0)
		return -1;
	else
		return st.st_mtime;
}
