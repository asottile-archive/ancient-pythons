#ifndef Py_INTRCHECK_H
#define Py_INTRCHECK_H
#ifdef __cplusplus
extern "C" {
#endif

extern DL_IMPORT(int) PyOS_InterruptOccurred Py_PROTO((void));
extern DL_IMPORT(void) PyOS_InitInterrupts Py_PROTO((void));
DL_IMPORT(void) PyOS_AfterFork Py_PROTO((void));

#ifdef __cplusplus
}
#endif
#endif /* !Py_INTRCHECK_H */
