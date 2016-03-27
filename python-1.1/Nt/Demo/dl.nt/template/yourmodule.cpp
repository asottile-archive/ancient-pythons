/*************************************************************************

	This is a generic "template" file for building DLL extension
	files for Python on NT.

	Replace all occurences of "your" with something appropriate!
	Do this in the makefile too!

	This could be a C file, but the Python make will force the build
	as C++.  This is due to a limitation in DLL's.  Apparently, when 
	dynamically linking to _variables_ (which Python must) a C++ compiler
	must be used, as the C compiler does not guarantee correct initialisation
	of static data (or some such!  Anyway, it gives compile errors!)

*************************************************************************/

/* yourmodule.cpp -- module for something */

#include "windows.h"

// windows seems to define these macros too.
#undef INCREF
#undef DECREF

#include "allobjects.h"
#include "modsupport.h"

static object *your_module_error;

static object *
your_python_method(object * self, object * args)
{
	INCREF(None);
	return None;
}

/* List of functions exported by this module */
static struct methodlist your_functions[] = {
	{"your_python_method",		(method)your_python_method},
	{NULL,			NULL}		 /* Sentinel */
};


void
inityour(void)
{
	object *dict, *module;
	module = initmodule("your", your_functions);
	dict = getmoduledict(module);
	your_module_error = newstringobject("your error");
	dictinsert(dict, "error", your_module_error);
}
