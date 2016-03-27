#ifndef Py_EVAL_H
#define Py_EVAL_H
#ifdef __cplusplus
extern "C" {
#endif

/* Interface to execute compiled code */

DL_IMPORT(PyObject *) PyEval_EvalCode Py_PROTO((PyCodeObject *, PyObject *, PyObject *));

#ifdef __cplusplus
}
#endif
#endif /* !Py_EVAL_H */
