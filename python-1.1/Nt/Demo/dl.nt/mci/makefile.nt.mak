# Replace the next to lines as appropriate.
module=mcimodule
pythondir=..\..\..\

BUILD_DL=1
!include <$(pythondir)\make.nt.in>
#override the srcdir spec.
srcdir=$(pythondir)

lcustom=winmm.lib


all: $(module).dll

$(module).dll : $(module).obj

.ignore:

clean:
	del *.obj *.lib *.exp *.pdb *.pch 2>nul	# some may not exist - who cares!

clobber: clean
	del *.dll
