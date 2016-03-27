!include <..\make.nt.in>


OBJS=		accessobject.obj \
		classobject.obj fileobject.obj floatobject.obj \
		frameobject.obj funcobject.obj intobject.obj listobject.obj \
		longobject.obj mappingobject.obj methodobject.obj \
		moduleobject.obj object.obj rangeobject.obj stringobject.obj \
		tupleobject.obj typeobject.obj

SRCS=		accessobject.c \
		classobject.c fileobject.c floatobject.c \
		frameobject.c funcobject.c intobject.c listobject.c \
		longobject.c mappingobject.c methodobject.c \
		moduleobject.c object.c rangeobject.c stringobject.c \
		tupleobject.c typeobject.c

XLIB=		Objects.lib

# === Rules ===

all:		$(XLIB)

$(XLIB):	$(OBJS)
		$(libmgr) -out:$(XLIB) $(OBJS)

.ignore:

clean: 
	del *.obj *.lib *.pdb 2>nul

clobber: clean

# DO NOT DELETE THIS LINE -- mkdep uses it.
# DO NOT PUT ANYTHING AFTER THIS LINE, IT WILL GO AWAY.
# IF YOU PUT ANYTHING HERE IT WILL GO AWAY
