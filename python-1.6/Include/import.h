#ifndef Py_IMPORT_H
#define Py_IMPORT_H
#ifdef __cplusplus
extern "C" {
#endif

/* Module definition and import interface */

DL_IMPORT(long) PyImport_GetMagicNumber Py_PROTO((void));
DL_IMPORT(PyObject *) PyImport_ExecCodeModule Py_PROTO((char *name, PyObject *co));
DL_IMPORT(PyObject *) PyImport_ExecCodeModuleEx Py_PROTO((
	char *name, PyObject *co, char *pathname));
DL_IMPORT(PyObject *) PyImport_GetModuleDict Py_PROTO((void));
DL_IMPORT(PyObject *) PyImport_AddModule Py_PROTO((char *name));
DL_IMPORT(PyObject *) PyImport_ImportModule Py_PROTO((char *name));
DL_IMPORT(PyObject *) PyImport_ImportModuleEx Py_PROTO((
	char *name, PyObject *globals, PyObject *locals, PyObject *fromlist));
DL_IMPORT(PyObject *) PyImport_Import Py_PROTO((PyObject *name));
DL_IMPORT(PyObject *) PyImport_ReloadModule Py_PROTO((PyObject *m));
DL_IMPORT(void) PyImport_Cleanup Py_PROTO((void));
DL_IMPORT(int) PyImport_ImportFrozenModule Py_PROTO((char *));

extern DL_IMPORT(PyObject *)_PyImport_FindExtension Py_PROTO((char *, char *));
extern DL_IMPORT(PyObject *)_PyImport_FixupExtension Py_PROTO((char *, char *));

struct _inittab {
	char *name;
	void (*initfunc)();
};

extern DL_IMPORT(struct _inittab *) PyImport_Inittab;

extern DL_IMPORT(int) PyImport_AppendInittab Py_PROTO((char *name, void (*initfunc)()));
extern DL_IMPORT(int) PyImport_ExtendInittab Py_PROTO((struct _inittab *newtab));

struct _frozen {
	char *name;
	unsigned char *code;
	int size;
};

/* Embedding apps may change this pointer to point to their favorite
   collection of frozen modules: */

extern DL_IMPORT(struct _frozen *) PyImport_FrozenModules;

#ifdef __cplusplus
}
#endif
#endif /* !Py_IMPORT_H */
