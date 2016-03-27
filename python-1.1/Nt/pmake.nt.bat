@echo off

: Copied from make.nt.bat

: check for MSVC (save passing on cmd line)
if exist \msvcnt\. set MSVC=1
if exist c:\msvcnt\. set MSVC=1

set makefile=makefile.nt.mak
start "Python build - Parser"  /dParser  nmake /nologo /F %makefile% %1 %2 %3 %4 %5 %6 %7 %8 %9
start "Python build - Objects" /dObjects nmake /nologo /F %makefile% %1 %2 %3 %4 %5 %6 %7 %8 %9
start "Python build - Python" /dPython nmake /nologo /F %makefile% %1 %2 %3 %4 %5 %6 %7 %8 %9

set subdirs=Modules
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
