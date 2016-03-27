# Replace the next two lines as appropriate.
module=yourmodule
pythondir=..\..\..\

BUILD_DL=1
PCH=0				# for 1 module, small builds often not worth it.

!include <$(pythondir)\make.nt.in>
#override the srcdir spec.
srcdir=$(pythondir)


lcustom=			# if hitting windows itself, probably want $(guilibs)
ccustom=			# no real need.

all: $(module).dll

$(module).dll : $(module).obj

.ignore:

clean:
	del *.obj *.lib *.exp *.pdb *.pch 2>nul	# some may not exist - who cares!

clobber: clean
	del *.dll
