#ifndef Py_PGEN_H
#define Py_PGEN_H
#ifdef __cplusplus
extern "C" {
#endif

/* Parser generator interface */

extern grammar *meta_grammar Py_PROTO((void));

struct _node;
extern grammar *pgen Py_PROTO((struct _node *));

#ifdef __cplusplus
}
#endif
#endif /* !Py_PGEN_H */
