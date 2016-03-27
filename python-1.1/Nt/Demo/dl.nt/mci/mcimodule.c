/***********************************************************

******************************************************************/

/* mci.c -- module for interface into Win32's MCI interface. */
#include "windows.h"

#undef INCREF
#undef DECREF

#include "allobjects.h"
#include "modsupport.h"

static object *mci_module_error;

/* Send an MCI "play" command */
static object *
py_mci_send(object * self, object * args)
{
	DWORD ret;
	char * cmd;
	char retString[128];
	object *retObj;

	if (!getargs(args, "s", &cmd))
		return (NULL);

	ret = mciSendString(cmd, retString, sizeof(retString), 0);
	if (ret!=0)
	{
		if (!mciGetErrorString(ret, retString, sizeof(retString)))
			sprintf(retString,"unknown MCI error (%ld)", (long)ret);
	    err_setstr(mci_module_error, retString);
		return NULL;
	}
	if (retString[0]=='\0')
	{
		INCREF(None);
		retObj = None;
	}
	else
		retObj = mkvalue("s", retString);
	return retObj;
}


/* List of functions exported by this module */
static struct methodlist mci_functions[] = {
	{"send",		(method)py_mci_send},
	{NULL,			NULL}		 /* Sentinel */
};


void
initmci(void)
{
  object *dict, *module;
  module = initmodule("mci", mci_functions);
  dict = getmoduledict(module);
  mci_module_error = newstringobject("mci error");
  dictinsert(dict, "error", mci_module_error);
}
