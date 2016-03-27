#ifndef Py_PROTO_H
#define Py_PROTO_H
#ifdef __cplusplus
extern "C" {
#endif

#ifdef HAVE_PROTOTYPES
#define Py_PROTO(x) x
#else
#define Py_PROTO(x) ()
#endif

#ifndef Py_FPROTO
#define Py_FPROTO(x) Py_PROTO(x)
#endif

#ifdef __cplusplus
}
#endif

#endif /* !Py_PROTO_H */
