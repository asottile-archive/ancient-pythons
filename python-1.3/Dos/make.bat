@if "%1" == "win16" goto QW
@if "%1" == "qw" goto QW
@if "%1" == "dos32" goto GCC
@if "%1" == "dj" goto GCC
@
@echo Must specify target for make (win16 or dos32)
@goto Stop
@
:QW
nmake -fpython.mak TARGET=win16 %2 %3 %4 %5 %6 %7 %8 %9
@goto Stop
@
:GCC
nmaker -fpython.mak TARGET=dos32 %2 %3 %4 %5 %6 %7 %8 %9
@
:Stop
