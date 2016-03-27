libs = :Python:lib.o :Mac:lib.o :Modules:lib.o :Objects:lib.o :Parser:lib.o
depend = {libs}

PythonTool Ä {depend}
	link {LinkOptions} -o PythonTool -t 'MPST' -c "MPS " ¶
		{libs} ¶
		"{Libraries}Runtime.o" ¶
		"{Libraries}Interface.o" ¶
		"{CLibraries}StdCLib.o" ¶
		"{CLibraries}CSANELib.o" ¶
		"{CLibraries}Math.o" 

clean	Ä
	Delete -i PythonTool
