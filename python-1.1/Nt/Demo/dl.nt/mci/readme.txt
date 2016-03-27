Notes for MCI.


mcimodule.c is a demo of dynamic loading under the NT environment.  It has a _very_ basic interface into the Windows MCI interface.

Using the Extension Module:
* First the extension module must be built.  This will create mcimodule.dll.
* mcimodule.dll must be in a directory pointed at by the PYTHONPATH environment variable (being on the PATH is not sufficient (or required!))
* start python.
* enter the command 'import mci' (without quotes) and press enter.
* enter the command 'mci.send("play c:/winnt/chord.wav")' <enter> (substitute your windows/WindowsNT directory if it is not as above)
* If you have an .AVI file available, enter the command above, but with the AVI filename, to see Video for Windows.
* Look up the "mciSendString()" command in the Win32 SDK help to see what else you can do with the MCI interface.

Building the Module:
Simply run the command:
	nmake /f makefile.nt.mak
or
	nmake /f makefile.nt.mak NODEBUG=1
for the optimised, non-debug version.

- eof -
