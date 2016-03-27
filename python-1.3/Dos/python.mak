#
# some notes on the Makefile:
#
# We support both windows (QuickWin) and gcc 32-bit executables.  The parser
# generator (pgen) is always built as a 32-bit executable; this implies a
# special build target and recursive invocation of make.  (This is not yet
# implemented; If you change the grammar you must first do a build with gcc.)
#

BINDIR = ..\bin
LIBDIR = ..\lib
OBJDIR = ..\obj\$(TARGET)


#
# define object modules
#

PYOBJECTS = \
	$(OBJDIR)\config.$(OBJ) \
	$(OBJDIR)\acceler.$(OBJ) \
	$(OBJDIR)\accesobj.$(OBJ) \
	$(OBJDIR)\arraymod.$(OBJ) \
	$(OBJDIR)\bltinmod.$(OBJ) \
	$(OBJDIR)\ceval.$(OBJ) \
	$(OBJDIR)\classobj.$(OBJ) \
	$(OBJDIR)\compile.$(OBJ) \
	$(OBJDIR)\dosmod.$(OBJ) \
	$(OBJDIR)\errors.$(OBJ) \
	$(OBJDIR)\fileobj.$(OBJ) \
	$(OBJDIR)\floatobj.$(OBJ) \
	$(OBJDIR)\frameobj.$(OBJ) \
	$(OBJDIR)\funcobj.$(OBJ) \
	$(OBJDIR)\getmtime.$(OBJ) \
	$(OBJDIR)\getopt.$(OBJ) \
	$(OBJDIR)\graminit.$(OBJ) \
	$(OBJDIR)\grammar1.$(OBJ) \
	$(OBJDIR)\import.$(OBJ) \
	$(OBJDIR)\intobj.$(OBJ) \
	$(OBJDIR)\intrchk.$(OBJ) \
	$(OBJDIR)\listnode.$(OBJ) \
	$(OBJDIR)\listobj.$(OBJ) \
	$(OBJDIR)\lispmod.$(OBJ) \
	$(OBJDIR)\longobj.$(OBJ) \
	$(OBJDIR)\mapobj.$(OBJ) \
	$(OBJDIR)\marshal.$(OBJ) \
	$(OBJDIR)\mathmod.$(OBJ) \
	$(OBJDIR)\methobj.$(OBJ) \
	$(OBJDIR)\modsupp.$(OBJ) \
	$(OBJDIR)\modulobj.$(OBJ) \
	$(OBJDIR)\node.$(OBJ) \
	$(OBJDIR)\object.$(OBJ) \
	$(OBJDIR)\parser.$(OBJ) \
	$(OBJDIR)\parsemod.$(OBJ) \
	$(OBJDIR)\parsetok.$(OBJ) \
	$(OBJDIR)\pymain.$(OBJ) \
	$(OBJDIR)\pyrun.$(OBJ) \
	$(OBJDIR)\rangeobj.$(OBJ) \
	$(OBJDIR)\readline.$(OBJ) \
	$(OBJDIR)\regexmod.$(OBJ) \
	$(OBJDIR)\regexpr.$(OBJ) \
	$(OBJDIR)\rotormod.$(OBJ) \
	$(OBJDIR)\strobj.$(OBJ) \
	$(OBJDIR)\stropmod.$(OBJ) \
	$(OBJDIR)\strctmem.$(OBJ) \
	$(OBJDIR)\strctmod.$(OBJ) \
	$(OBJDIR)\sysmod.$(OBJ) \
	$(OBJDIR)\system.$(OBJ) \
	$(OBJDIR)\timemod.$(OBJ) \
	$(OBJDIR)\tokenize.$(OBJ) \
	$(OBJDIR)\tracebak.$(OBJ) \
	$(OBJDIR)\tupleobj.$(OBJ) \
	$(OBJDIR)\typeobj.$(OBJ) \
	$(OBJDIR)\version.$(OBJ) \

GENOBJECTS = \
	$(OBJDIR)\acceler.$(OBJ) \
	$(OBJDIR)\bitset.$(OBJ) \
	$(OBJDIR)\grammar1.$(OBJ) \
	$(OBJDIR)\intrchk.$(OBJ) \
	$(OBJDIR)\listnode.$(OBJ) \
	$(OBJDIR)\node.$(OBJ) \
	$(OBJDIR)\parser.$(OBJ) \
	$(OBJDIR)\parsetok.$(OBJ) \
	$(OBJDIR)\tokenize.$(OBJ) \
	$(OBJDIR)\firstset.$(OBJ) \
	$(OBJDIR)\grammar.$(OBJ) \
	$(OBJDIR)\metagram.$(OBJ) \
	$(OBJDIR)\pgen.$(OBJ) \
	$(OBJDIR)\pgenmain.$(OBJ) \
	$(OBJDIR)\prntgram.$(OBJ) \


#
# build python.exe, 32 bit DOS extended GCC. 
#

!if "$(TARGET)" == "dos32"

!if "$(MAKE)" != "NMAKER"
!error You must use real-mode make with GCC.
!endif

CC       = gcc
AR       = ar
CPPFLAGS = -DHAVE_CONFIG_H
CFLAGS   = -O2
PYTHON   = $(BINDIR)\python.exe
CLEAN    = pgen.exe graminit.[ch]
OBJ      = o

{}.c{$(OBJDIR)}.$(OBJ) :
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

all : init $(PYTHON)
$(PYTHON) : $(PYOBJECTS)
	$(CC) $(CFLAGS) @<< -o python.out -lm
$**
<<
	coff2exe python.out
	mv python.exe $(BINDIR)

pgen.exe : $(GENOBJECTS)
	$(CC) $(CFLAGS) @<< -o pgen
$**
<<
	strip pgen
	coff2exe pgen
	del pgen


# The dependencies for graminit.[ch] are not turned on in the
# distributed Makefile because the files themselves are distributed.
# Turn them on if you want to hack the grammar.

graminit.c:	Grammar pgen.exe
		pgen Grammar

# One call to python_gen writes both files, so here's a fake dependency:
graminit.h:	graminit.c


!endif


#
# build 16 bit windows python DLL, and python executable.
#	(Actually we use QuickWin for now...)
#

!if "$(TARGET)" == "win16"

CC        = cl
AR        = lib
BSCFLAGS  = -Es
CPPFLAGS  = -DQUICKWIN -DHAVE_CONFIG_H
CFLAGS    = -nologo -Fr$(OBJDIR)\ -AL
RELCFLAGS = -G3fy -Owceilot
DBGCFLAGS = -Zi -G2f -Fd$(OBJDIR)\python.pdb
LDFLAGS   = /farcall /onerror:noexe /noignorecase
PYTHONLIB = $(LIBDIR)\python.lib
PYTHON    = $(BINDIR)\pythonw.exe
CLEAN     = python.bsc
OBJ       = obj

!if "$(DEBUG)" == "true"
CFLAGS = $(CFLAGS) $(DBGCFLAGS)

!else
CFLAGS = $(CFLAGS) $(RELCFLAGS)

!endif


{}.c{$(OBJDIR)}.$(OBJ) :
	$(CC) $(CPPFLAGS) $(CFLAGS) -Mq -Fo$@ -c $<

all : init $(PYTHON)
$(PYTHON) : $(PYOBJECTS)
	$(CC) $(CFLAGS) -Mq -Fe$@ $** toolhelp.lib -link $(LDFLAGS)
	bscmake $(BSCFLAGS) -o python.bsc $(OBJDIR)\*.sbr

_SOURCE = $(PYOBJECTS:..\obj\win16=.)
SOURCES = $(_SOURCE:.obj=.c)

rebuild_sdb :
	cl -Zs -Fr$(OBJDIR)\ $(SOURCES)
	bscmake $(BSCFLAGS) -o python.bsc $(OBJDIR)\*.sbr

$(OBJDIR)\system.obj : system.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -GA -GEd -Fo$@ -c $(@B).c

!endif


!ifndef OBJ
!error TARGET must be dos32 or win16.
!endif


#
# Use this target to build directories
#

init :
	@-mkdir $(OBJDIR)


clean :
	rm -rf $(OBJDIR) $(PYTHON) $(PYTHONLIB) $(CLEAN)


$(OBJDIR)\ceval.$(OBJ):		graminit.h
$(OBJDIR)\compile.$(OBJ):	graminit.h
$(OBJDIR)\bltinmod.$(OBJ):	graminit.h
$(OBJDIR)\import.$(OBJ):	graminit.h
$(OBJDIR)\parsemod.$(OBJ):	graminit.h
$(OBJDIR)\pyrun.$(OBJ):		graminit.h
