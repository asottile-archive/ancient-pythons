#ifndef Py_MODULEOBJECT_H
#define Py_MODULEOBJECT_H
#ifdef __cplusplus
extern "C" {
#endif

/* Module object interface */

extern DL_IMPORT(PyTypeObject) PyModule_Type;

#define PyModule_Check(op) ((op)->ob_type == &PyModule_Type)

extern DL_IMPORT(PyObject *) PyModule_New Py_PROTO((char *));
extern DL_IMPORT(PyObject *) PyModule_GetDict Py_PROTO((PyObject *));
extern DL_IMPORT(char *) PyModule_GetName Py_PROTO((PyObject *));
extern DL_IMPORT(char *) PyModule_GetFilename Py_PROTO((PyObject *));
extern DL_IMPORT(void) _PyModule_Clear Py_PROTO((PyObject *));

#ifdef __cplusplus
}
#endif
#endif /* !Py_MODULEOBJECT_H */
