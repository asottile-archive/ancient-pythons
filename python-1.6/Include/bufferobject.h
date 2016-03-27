#ifndef Py_BUFFEROBJECT_H
#define Py_BUFFEROBJECT_H
#ifdef __cplusplus
extern "C" {
#endif

/* Buffer object interface */

/* Note: the object's structure is private */


extern DL_IMPORT(PyTypeObject) PyBuffer_Type;

#define PyBuffer_Check(op) ((op)->ob_type == &PyBuffer_Type)

#define Py_END_OF_BUFFER	(-1)

extern DL_IMPORT(PyObject *) PyBuffer_FromObject Py_PROTO((PyObject *base, int offset, int size));
extern DL_IMPORT(PyObject *) PyBuffer_FromReadWriteObject Py_PROTO((PyObject *base, int offset, int size));

extern DL_IMPORT(PyObject *) PyBuffer_FromMemory Py_PROTO((void *ptr, int size));
extern DL_IMPORT(PyObject *) PyBuffer_FromReadWriteMemory Py_PROTO((void *ptr, int size));

extern DL_IMPORT(PyObject *) PyBuffer_New Py_PROTO((int size));

#ifdef __cplusplus
}
#endif
#endif /* !Py_BUFFEROBJECT_H */

