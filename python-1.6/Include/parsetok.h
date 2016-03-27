#ifndef Py_PARSETOK_H
#define Py_PARSETOK_H
#ifdef __cplusplus
extern "C" {
#endif

/* Parser-tokenizer link interface */

typedef struct {
	int error;
	char *filename;
	int lineno;
	int offset;
	char *text;
} perrdetail;

extern DL_IMPORT(node *) PyParser_ParseString Py_PROTO((char *, grammar *, int, perrdetail *));
extern DL_IMPORT(node *) PyParser_ParseFile Py_PROTO((FILE *, char *, grammar *, int,
			    char *, char *, perrdetail *));

#ifdef __cplusplus
}
#endif
#endif /* !Py_PARSETOK_H */
