!include <..\make.nt.in>

OBJS=		\
		bltinmodule.obj \
		ceval.obj cgensupport.obj compile.obj \
		errors.obj \
		frozenmain.obj \
		getargs.obj getmtime.obj graminit.obj \
		import.obj \
		marshal.obj modsupport.obj mystrtoul.obj \
		pythonmain.obj pythonrun.obj \
		structmember.obj sysmodule.obj \
		traceback.obj \
		getopt.obj \
		sigcheck.obj \
		$(LIBOBJS)

XLIB=		Python.lib

all:		$(XLIB)

$(XLIB):	$(OBJS)
		$(libmgr) -out:$(XLIB) $(OBJS)

.ignore:

clean:
		del *.obj *.lib *~ *.pdb 2>nul

clobber: clean
