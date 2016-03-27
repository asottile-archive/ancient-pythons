#ifndef Py_TRACEBACK_H
#define Py_TRACEBACK_H
#ifdef __cplusplus
extern "C" {
#endif

/* Traceback interface */

struct _frame;

DL_IMPORT(int) PyTraceBack_Here Py_PROTO((struct _frame *));
DL_IMPORT(PyObject *) PyTraceBack_Fetch Py_PROTO((void));
DL_IMPORT(int) PyTraceBack_Store Py_PROTO((PyObject *));
DL_IMPORT(int) PyTraceBack_Print Py_PROTO((PyObject *, PyObject *));

/* Reveale traceback type so we can typecheck traceback objects */
extern DL_IMPORT(PyTypeObject) PyTraceBack_Type;
#define PyTraceBack_Check(v) ((v)->ob_type == &PyTraceBack_Type)

#ifdef __cplusplus
}
#endif
#endif /* !Py_TRACEBACK_H */
