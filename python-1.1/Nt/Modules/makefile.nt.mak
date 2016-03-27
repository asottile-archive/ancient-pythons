# This makefile builds the binaries
#
# Almost all the code goes into Python.dll, with only a small amount in
# Python.EXE.
#
# This makefile also builds socketmodule.dll
#
# When Python.dll is built, Pythondefs.lib is also built.  This file
# contains references into the DLL, and must be distributed with Python.dll
# for developers of extension modules.
!include <..\make.nt.in>

OBJS=  arraymodule.obj mathmodule.obj md5module.obj md5c.obj \
		posixmodule.obj parsermodule.obj regexmodule.obj regexpr.obj \
		rotormodule.obj	stropmodule.obj structmodule.obj \
		timemodule.obj

lcustom=$(guilibsdll)

XLIB=		Modules.lib

MYLIBS=		$(XLIB) \
		..\Python\Python.lib \
		..\Objects\Objects.lib \
		..\Parser\Parser.lib

all:		..\Python.exe ..\Python.dll ..\socketmodule.dll

$(XLIB):	$(OBJS)
		$(libmgr) -out:$(XLIB) $(OBJS)

..\Python.exe : pythoncon.obj $(python_defs_lib)
	$(linker) -out:$*.exe pythoncon.obj -subsystem:console $(ldebug) $(python_defs_lib) $(conlibs)

$(python_defs_lib) $(python_defs_exp): python.nt.def
	$(implib) -out:$*.lib -machine:$(CPU) -def:python.nt.def

# Note we have specified a DLL entrypoint, to guarantee Python's init.
# Currently not required to be specified, but will be if we move 
# to multi-thread DLL.
..\Python.dll : $(python_defs_exp) dl.nt.obj config.nt.obj $(MYLIBS)
	link -out:$*.dll -dll config.nt.obj dl.nt.obj $(python_defs_exp)\
		-entry:_DllMainCRTStartup$(DLLENTRY) $(ldebug) $(MYLIBS) \
		 $(lcustom)

dl.nt.obj: $*.c
		$(CC) $(cflags) $(cdebug) $(cinclude) $(pythonopts) $*.c

config.nt.obj:	$*.c
		$(CC) $(cflags) $(cdebug) $(cinclude) $(pythonopts) /DNO_MAIN $*.c

pythoncon.obj: config.nt.c
		$(CC) $(cflags) $(cdebug) $(cinclude) $(pythonopts) /Fopythoncon.obj /DNO_MODULES config.nt.c

#############
# sockets DLL

..\socketmodule.dll: socketmodule.obj ..\Python.dll
	link -dll -out:$*.dll socketmodule.obj -implib:socketmodule.lib wsock32.lib -entry:_DllMainCRTStartup$(DLLENTRY) $(ldebug) /EXPORT:initsocket $(lcustom) $(python_defs_lib)

# Build as C++ module!
socketmodule.obj: socketmodule.c
	$(cc) $(cflags) $(ccustom) $(cdebug) $(cinclude) $(cpch) $(pythonopts) /DUSE_DL_IMPORT /Tp $*.c



.ignore:

clean :
		del *.obj *.lib *~ *.vcw *.wsp ..\*.vcw ..\*.wsp *.pdb 2>nul

clobber: clean
		del ..\python.dll ..\python.exe pythondefs.* 2>nul
		cd..
		del socketmodule.exp socketmodule.lib socketmodule.dll 2>nul
		del *.pyc /s 2>nul
