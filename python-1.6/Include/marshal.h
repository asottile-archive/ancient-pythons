#ifndef Py_MARSHAL_H
#define Py_MARSHAL_H
#ifdef __cplusplus
extern "C" {
#endif

/* Interface for marshal.c */

DL_IMPORT(void) PyMarshal_WriteLongToFile Py_PROTO((long, FILE *));
DL_IMPORT(void) PyMarshal_WriteShortToFile Py_PROTO((int, FILE *));
DL_IMPORT(void) PyMarshal_WriteObjectToFile Py_PROTO((PyObject *, FILE *));
DL_IMPORT(PyObject *) PyMarshal_WriteObjectToString Py_PROTO((PyObject *));

DL_IMPORT(long) PyMarshal_ReadLongFromFile Py_PROTO((FILE *));
DL_IMPORT(int) PyMarshal_ReadShortFromFile Py_PROTO((FILE *));
DL_IMPORT(PyObject *) PyMarshal_ReadObjectFromFile Py_PROTO((FILE *));
DL_IMPORT(PyObject *) PyMarshal_ReadObjectFromString Py_PROTO((char *, int));

#ifdef __cplusplus
}
#endif
#endif /* !Py_MARSHAL_H */
