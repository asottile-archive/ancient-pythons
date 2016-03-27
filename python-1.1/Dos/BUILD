This is a (slightly edited) mail from Amrit, explaining how to build
Python on DOS.  See also the files "make.bat" and "python.mak".

From: amrit@xvt.com (Consultant)
Subject: Re: Python 1.0.2 on DOS
To: Guido.van.Rossum@cwi.nl
Date: Mon, 16 May 1994 11:50:22 -0600 (MDT)

I have a Makefile, but I didn't submit it because I'm still hanging on
to the pre-1.0 build procedures.  Having everything in one directory
makes things easier to build and work with in Microsoft's PWB.  Also,
there is no reason to split things up when 90% of the optional modules
have no meaning in DOS, so the build area is much smaller than on your
typical UNIX box.

I also rename all of the source files that are longer than 8
characters with a script before I build.  This is because Microsoft
NMAKE considers the file dependency "intobject.c" and the real file,
"intobje.c" different as far a dependency checking goes.  (Another
alternative would be to list "intobje.o" as the target rather than
intobject.o; what I did was just rename intobject.c to intobj.c)

The makefile can build a debug QuickWin executable, an optimized
QuickWin executable, or a DOS extended python executable.

However, this Makefile is a start.  It already takes care of a lot of
stuff that you would have to re-invent.  (such as dealing with the
fact that gcc objects end with ".o" and the standard DOS suffix is
".obj")

The makefile assumes the following directory structure:

    python
	- bin
	- obj
	- src

The bin and obj directory should exist before make is invoked.  A
script, make.bat, runs nmake with the appropriate flags to build the
DOS or QuickWin version.  The microsoft version generates browser
information automatically.
