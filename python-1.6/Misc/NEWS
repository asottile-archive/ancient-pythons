What's new in release 1.6?
==========================

Below is a list of all relevant changes since release 1.5.2.  Older
changes are in the file HISTORY.

--Guido van Rossum (home page: http://www.pythonlabs.com/~guido/)

======================================================================

Source Incompatibilities
------------------------

Several small incompatible library changes may trip you up:

  - The append() method for lists can no longer be invoked with more
  than one argument.  This used to append a single tuple made out of
  all arguments, but was undocumented.  To append a tuple, use
  e.g. l.append((a, b, c)).

  - The connect(), connect_ex() and bind() methods for sockets require
  exactly one argument.  Previously, you could call s.connect(host,
  port), but this was undocumented. You must now write
  s.connect((host, port)).

  - The str() and repr() functions are now different more often.  For
  long integers, str() no longer appends a 'L'.  Thus, str(1L) == '1',
  which used to be '1L'; repr(1L) is unchanged and still returns '1L'.
  For floats, repr() now gives 17 digits of precision, to ensure no
  precision is lost (on all current hardware).

  - The -X option is gone.  Built-in exceptions are now always
  classes.  Many more library modules also have been converted to
  class-based exceptions.


Binary Incompatibilities
------------------------

- Third party extensions built for Python 1.5.x cannot be used with
Python 1.6; these extensions will have to be rebuilt for Python 1.6.

- On Windows, attempting to import a third party extension built for
Python 1.5.x results in an immediate crash; there's not much we can do
about this.  Check your PYTHONPATH environment variable!


Overview of Changes since 1.5.2
-------------------------------

For this overview, I have borrowed from the document "What's New in
Python 2.0" by Andrew Kuchling and Moshe Zadka:
http://starship.python.net/crew/amk/python/writing/new-python/.

There are lots of new modules and lots of bugs have been fixed.  A
list of all new modules is included below.

Probably the most pervasive change is the addition of Unicode support.
We've added a new fundamental datatype, the Unicode string, a new
build-in function unicode(), an numerous C APIs to deal with Unicode
and encodings.  See the file Misc/unicode.txt for details, or
http://starship.python.net/crew/lemburg/unicode-proposal.txt.

Two other big changes, related to the Unicode support, are the
addition of string methods and (yet another) new regular expression
engine.

  - String methods mean that you can now say s.lower() etc. instead of
  importing the string module and saying string.lower(s) etc.  One
  peculiarity is that the equivalent of string.join(sequence,
  delimiter) is delimiter.join(sequence).  Use " ".join(sequence) for
  the effect of string.join(sequence); to make this more readable, try
  space=" " first.  Note that the maxsplit argument defaults in
  split() and replace() have changed from 0 to -1.

  - The new regular expression engine, SRE by Fredrik Lundh, is fully
  backwards compatible with the old engine, and is in fact invoked
  using the same interface (the "re" module).  You can explicitly
  invoke the old engine by import pre, or the SRE engine by importing
  sre.  SRE is faster than pre, and supports Unicode (which was the
  main reason to put effort in yet another new regular expression
  engine -- this is at least the fourth!).


Other Changes
-------------

Other changes that won't break code but are nice to know about:

Deleting objects is now safe even for deeply nested data structures.

Long/int unifications: long integers can be used in seek() calls, as
slice indexes.

String formatting (s % args) has a new formatting option, '%r', which
acts like '%s' but inserts repr(arg) instead of str(arg). (Not yet in
alpha 1.)

Greg Ward's "distutils" package is included: this will make
installing, building and distributing third party packages much
simpler.

There's now special syntax that you can use instead of the apply()
function.  f(*args, **kwds) is equivalent to apply(f, args, kwds).
You can also use variations f(a1, a2, *args, **kwds) and you can leave
one or the other out: f(*args), f(**kwds).

The built-ins int() and long() take an optional second argument to
indicate the conversion base -- of course only if the first argument
is a string.  This makes string.atoi() and string.atol() obsolete.
(string.atof() was already obsolete).

When a local variable is known to the compiler but undefined when
used, a new exception UnboundLocalError is raised.  This is a class
derived from NameError so code catching NameError should still work.
The purpose is to provide better diagnostics in the following example:
  x = 1
  def f():
      print x
      x = x+1
This used to raise a NameError on the print statement, which confused
even experienced Python programmers (especially if there are several
hundreds of lines of code between the reference and the assignment to
x :-).

You can now override the 'in' operator by defining a __contains__
method.  Note that it has its arguments backwards: x in a causes
a.__contains__(x) to be called.  That's why the name isn't __in__.

The exception AttributeError will have a more friendly error message,
e.g.: <code>'Spam' instance has no attribute 'eggs'</code>.  This may
<b>break code</b> that expects the message to be exactly the attribute
name.

Vladimir Marangozov designed more rational C APIs for allocating
memory.  See mymalloc.h.


New Modules in 1.6
------------------

UserString - base class for deriving from the string type.

distutils - tools for distributing Python modules.

robotparser - parse a robots.txt file, for writing web spiders.
(Moved from Tools/webchecker/.)

linuxaudiodev - audio for Linux.

mmap - treat a file as a memory buffer.  (Windows and Unix.)

sre - regular expressions (fast, supports unicode).  Currently, this
code is very rough.  Eventually, the re module will be reimplemented
using sre (without changes to the re API).

filecmp - supersedes the old cmp.py and dircmp.py modules.

tabnanny - check Python sources for tab-width dependance.  (Moved from
Tools/scripts/.)

urllib2 - new and improved but incompatible version of urllib (still
experimental).

zipfile - read and write zip archives.

codecs - support for Unicode encoders/decoders.

unicodedata - provides access to the Unicode 3.0 database.

_winreg - Windows registry access.

encodings - package which provides a large set of standard codecs --
currently only for the new Unicode support. It has a drop-in extension
mechanism which allows you to add new codecs by simply copying them
into the encodings package directory. Asian codec support will
probably be made available as separate distribution package built upon
this technique and the new distutils package.


Changed Modules
---------------

readline, ConfigParser, cgi, calendar, posix, readline, xmllib, aifc,
chunk, wave, random, shelve, nntplib - minor enhancements.

socket, httplib, urllib - optional OpenSSL support (Unix only).

_tkinter - support for 8.0 up to 8.3.  Support for versions older than
8.0 has been dropped.

string - most of this module is deprecated now that strings have
methods.  This no longer uses the built-in strop module, but takes
advantage of the new string methods to provide transparent support for
both Unicode and ordinary strings.


Changes on Windows
------------------

The installer no longer runs a separate Tcl/Tk installer; instead, it
installs the needed Tcl/Tk files directly in the Python directory.  If
you already have a Tcl/Tk installation, this wastes some disk space
(about 4 Megs) but avoids problems with conflincting Tcl/Tk
installations, and makes it much easier for Python to ensure that
Tcl/Tk can find all its files.  Note: the alpha installers don't
include the documentation.

The Windows installer now installs by default in \Python16\ on the
default volume, instead of \Program Files\Python-1.6\.


Changed Tools
-------------

IDLE - complete overhaul.  See the <a href="../idle/">IDLE home
page</a> for more information.  (Python 1.6 alpha 1 will come with
IDLE 0.6.)

Tools/i18n/pygettext.py - Python equivalent of xgettext(1).  A message
text extraction tool used for internationalizing applications written
in Python.


Obsolete Modules
----------------

stdwin and everything that uses it.  (Get Python 1.5.2 if you need
it. :-)

soundex.  (Skip Montanaro has a version in Python but it won't be
included in the Python release.)

cmp, cmpcache, dircmp.  (Replaced by filecmp.)

dump.  (Use pickle.)

find.  (Easily coded using os.walk().)

grep.  (Not very useful as a library module.)

packmail.  (No longer has any use.)

poly, zmod.  (These were poor examples at best.)

strop.  (No longer needed by the string module.)

util.  (This functionality was long ago built in elsewhere).

whatsound.  (Use sndhdr.)


Detailed Changes from 1.6b1 to 1.6
----------------------------------

- Slight changes to the CNRI license.  A copyright notice has been
added; the requirement to indicate the nature of modifications now
applies when making a derivative work available "to others" instead of
just "to the public"; the version and date are updated.  The new
license has a new handle.

- Added the Tools/compiler package.  This is a project led by Jeremy
Hylton to write the Python bytecode generator in Python.

- The function math.rint() is removed.

- In Python.h, "#define _GNU_SOURCE 1" was added.

- Version 0.9.1 of Greg Ward's distutils is included (instead of
version 0.9).

- A new version of SRE is included.  It is more stable, and more
compatible with the old RE module.  Non-matching ranges are indicated
by -1, not None.  (The documentation said None, but the PRE
implementation used -1; changing to None would break existing code.)

- The winreg module has been renamed to _winreg.  (There are plans for
a higher-level API called winreg, but this has not yet materialized in
a form that is acceptable to the experts.)

- The _locale module is enabled by default.

- Fixed the configuration line for the _curses module.

- A few crashes have been fixed, notably <file>.writelines() with a
list containing non-string objects would crash, and there were
situations where a lost SyntaxError could dump core.

- The <list>.extend() method now accepts an arbitrary sequence
argument.

- If __str__() or __repr__() returns a Unicode object, this is
converted to an 8-bit string.

- Unicode string comparisons is no longer aware of UTF-16
encoding peculiarities; it's a straight 16-bit compare.

- The Windows installer now installs the LICENSE file and no longer
registers the Python DLL version in the registry (this is no longer
needed).  It now uses Tcl/Tk 8.3.2.

- A few portability problems have been fixed, in particular a
compilation error involving socklen_t.

- The PC configuration is slightly friendlier to non-Microsoft
compilers.


======================================================================
