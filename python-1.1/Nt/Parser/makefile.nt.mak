# NT Makefile for parser.
#
# NOTE: pgen is not built

!include <..\make.nt.in>

PARSEROBJS=	acceler.obj grammar1.obj intrcheck.obj listnode.obj \
			myreadline.obj node.obj parser.obj parsetok.obj \
			tokenizer.obj bitset.obj firstsets.obj grammar.obj \
			metagrammar.obj pgen.obj printgrammar.obj

PGENOBJS=	pgenmain.obj

OBJS=		$(PARSEROBJS)	# no PGENOBJS

PGEN=		pgen.exe

XLIB=		Parser.lib


all:		$(XLIB)  # $(PGEN)

$(XLIB):	$(PARSEROBJS)
		$(libmgr) -out:$(XLIB) $(PARSEROBJS)

$(PGEN):	$(PGENOBJS) $(XLIB)
		$(linker) $(linkdebug) crtdll.lib $(conflags) $(conlibs) \
			$(PGENOBJS) $(XLIB) -out:$(PGEN)

.ignore:

clean:
		del *.obj *.lib *.pdb 2> nul

clobber:	clean
		del $(PGEN) *.a tags TAGS 2>nul
