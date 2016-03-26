"""Module -- baw.py

This module contains extra utilities that I like to use in my personal
python scripts, such as startup.

functions defined in this module:

   system(command, backgroundp=0)
   execvpe(program, args)
   pexec(command)
   which(program)
   warn(formatstr, *args)

classes defined in this module:

exceptions defined in this module:

   CommandError
"""

############################################################
# preamble

__version__ = 'baw.py,v 1.9 1995/03/09 16:14:54 bwarsaw Exp'

import os

CommandError = 'CommandError'


############################################################
# system  -- Run a command in a subshell
#            input     : A command string, and a flag
#            output    : Command's stdout as a string
#            exceptions: CommandError if a system error occurred
#            effects   : Runs the command in a subshell, returning
#                        stdout as a string.  If an error occurred,
#                        this raises CommandError.  If the
#                        `backgroundp' flag is true, the entire
#                        process is run in the background.

def system(command, backgroundp=0):
    """Run a command in a subshell.

    Takes a COMMAND string and a BACKGROUNDP flag as arguments.  Uses
    /bin/sh as the subshell as required by POSIX.  Stderr messages are
    bound to stdout.  If the command exits with a non-zero status,
    'CommandError' is raised, which also returns the output string of
    the command.  If the command exits with a zero status, the result
    string is returned.

    If optional BACKGROUNDP flag is `true', then the entire process is
    run in the background and no status indication is returned.  Note
    that you should _not_ end command with an ampersand to put it in
    the background.  Use BACKGROUNDP instead.

    Changes to os.environ are not reflected in the environment of the
    executed command."""

    # Glom up the command string so that any stderr messages goes to
    # stdout.  POSIX guarantees that the shell used for the system
    # command is /bin/sh, or so I've been told.  This means that
    # sys.environ['SHELL'] need not be used and that the (...) 2&>1
    # syntax will always work.
    command = '(\n' + command + '\n) 2>&1'
    if backgroundp:
	os.system(command + ' & ')
	return None

    pipe = os.popen(command,  'r')
    result = pipe.read()
    status = pipe.close()
    # Strip a trailing newline from the result string. Mimics the
    # shell's backtick operator.
    if result[-1:] == '\n':
	result = result[:-1]
    # check the status and throw an exception if the command failed
    if not status:
	# command succeeded
	return result
    else:
	# command failed so raise an exception and return the error
	# message as the value of the exception
	raise CommandError, result


############################################################
# execvpe -- A cross between execve and execvp.
#            input     : a program and a list of args
#            output    : None
#            exceptions: os.error if an operating system error
#                        occurred
#            effects   : Searches os.environ['PATH'] for the command
#                        and executes it, passing os.environ to the
#                        new process.

def execvpe(program, args):
    """A cross between execve and execvp.

    Takes a program and a list of arguments to program.  Searches
    os.environ['PATH'] for the given program and executes it, passing
    it the os.environ dictionary.  If an error occurs, os.error is
    raised.  Otherwise, this function does not return."""

    # if path is an absolute or relative path of more than one
    # component, then just execve it without searching $PATH.
    head, tail = os.path.split(program)
    if head:
	os.execve(program, args, os.environ)
    else:
	# we have to search $PATH for the command
	try: envpath = os.environ['PATH']
	except KeyError: envpath = os.defpath

	# split the path
	import string
	pathdirs = string.splitfields(envpath, os.pathsep)

	# exec a file that is guaranteed to not exist so that we can
	# snag from the operating system the error number associated
	# with ENOENT.  Is it ever different?
	import tempfile
	try: os.execv(tempfile.mktemp(), ())
	except os.error, ENOENT: pass

	# initialize the error we will throw if the file isn't found
	exc, arg = os.error, ENOENT
	for dir in pathdirs:
	    fullname = os.path.join(dir, program)
	    try:
		os.execve(fullname, args, os.environ)
	    except os.error, (errno, msg):
		if errno != ENOENT:
		    exc, arg = os.error, (errno, msg)

	# we've checked every directory in the path. unsuccessful
	raise exc, arg


############################################################
# pexec -- A command that works similar to Perl4's exec
#          input     : A command string
#          output    : None
#          exceptions: No new exceptions defined
#          effects   : Transforms the python process into the command,
#                      using execvpe().  This only works on UNIX-like
#                      operating systems.  os.environ is correctly
#                      passed to the new process.  $PATH is searched
#                      for the command to execute.

def pexec(command):
    """Like Perl's exec command.

    Takes a command string as argument.  This is split into program
    and argument list suitable for running via execvpe (see also)."""

    import string
    args = string.split(command)

    program = args[0]
    # Semantics of execve and friends appears to be that the system
    # will overwrite argv[0] with the program name.  By leaving the
    # program name in args[0], we ensure that the passed arguments
    # show up in args[1:] in the called program.  This mimics what you
    # would see in a C program, but its unclear (to me at least)
    # whether this is POSIX defined behavior or not.
    execvpe(program, args)


############################################################
# which -- A command that mimics /bin/csh's which command
#          input:      A program name
#          output:     The path to program, or None if not found.
#          exceptions: No new exceptions defined
#          effects:    Search $PATH for program.

def which(program):
    """Like /bin/csh's which command.

    Takes a program name as an argument, and searches the PATH
    environment variable for the specified program.  If found, the
    full path to program is returned, otherwise None is returned."""
    # first figure out which PATH we're going to search
    try: path = os.environ['PATH']
    except KeyError: path = os.defpath

    # split the path
    import string
    import posix
    import stat
    pathdirs = string.splitfields(path, os.pathsep)

    found_p = None
    for dir in pathdirs:
	try:
	    found_p = os.path.join(dir, program)
	    st = posix.stat(found_p)
	    # check for both a regular file, and executable by owner
	    if not stat.S_ISREG(st[stat.ST_MODE]) or \
	       not (stat.S_IMODE(st[stat.ST_MODE]) & stat.S_IXUSR):
		# nope
		found_p = None
	except posix.error:
	    found_p = None

	# if a path was found, we're done
	if found_p: return found_p
    # never found
    return None


############################################################
# warn -- prints a warning to stderr.  style looks much more like
#         printf than print unfortunately. 
#
#         input:      A format string, and a variable number of arguments.
#         output:     None
#         exceptions: No new exceptions defined
#         effects:    Prints the message to stderr

def warn(formatstr, *args):
    """Prints an error message to sys.stderr.

    First argument is a FORMATSTRING suitable for printf; second
    and subsequent arguments are interpreted by the format string.
    There can be a variable number of subsequent arguments.

    It's too bad that this cannot have the same syntax as print."""
    import sys
    sys.stderr.write((formatstr % args) + "\n")
