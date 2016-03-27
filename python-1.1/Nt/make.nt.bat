@echo off

: Due to NMAKE being completely brain-dead, I decided to replace the
: Top Level makefile with a batch file.

: The primary reason was NMAKEs inability to recurse properly, and pasing
: params and macro defn's from toplevel to lower levels is nearly impossible.

: Common flags are handled by each lower level makefile including make.nt.in.

: This batch file only passes first 9 params to make.  Note that macro 
: definitions must be passed with quotes - eg: make_nt -a "NODEBUG=1" "MSVC=1"

: See the bottom of the file for some useful flags to nmake.

: check for MSVC (save passing on cmd line)
if exist \msvcnt\. set MSVC=1
if exist c:\msvcnt\. set MSVC=1

set subdirs=Parser Objects Python Modules
set makefile=makefile.nt.mak
for %%i in (%subdirs%) do echo %%i & title Python build - %%i & cd %%i & nmake /nologo /F %makefile% %1 %2 %3 %4 %5 %6 %7 %8 %9 & cd ..

: Clean up the environment.
set subdirs=
set makefile=
set MSVC=
title Command Prompt

: NOTE:  The following is pulled from winnt32.mak.  By passing these 
: arguments to this batch file, you will effect the specified build.

: Application Information Type         Invoke NMAKE
: ----------------------------         ------------
: For No Debugging Info                nmake nodebug=1
: For Working Set Tuner Info           nmake tune=1
: For Call Attributed Profiling Info   nmake profile=1
:
: Note: Working Set Tuner and Call Attributed Profiling is for available
:       for the Intel x86 and Pentium systems.
:
: Note: The three options above are mutually exclusive (you may use only
:       one to compile/link the application).
:
: Note: creating the environment variables NODEBUG, TUNE, and PROFILE is an
:       alternate method to setting these options via the nmake command line.
:
