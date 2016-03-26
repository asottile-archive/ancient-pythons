# os.py -- either mac, dos or posix depending on what system we're on.

# This exports:
# - all functions from either posix or mac, e.g., os.unlink, os.stat, etc.
# - os.path is either module posixpath or macpath
# - os.name is either 'posix' or 'mac'
# - os.curdir is a string representing the current directory ('.' or ':')
# - os.pardir is a string representing the parent directory ('..' or '::')
# - os.sep is the (or a most common) pathname separator ('/' or ':')

# Programs that import and use 'os' stand a better chance of being
# portable between different platforms.  Of course, they must then
# only use functions that are defined by all platforms (e.g., unlink
# and opendir), and leave all pathname manipulation to os.path
# (e.g., split and join).

_osindex = {
	  'posix': ('.', '..', '/'),
	  'dos':   ('.', '..', '\\'),
	  'mac':   (':', '::', ':'),
	  'nt':   ('.', '..', '\\'),
}

import sys
for name in _osindex.keys():
	if name in sys.builtin_module_names:
		curdir, pardir, sep = _osindex[name]
		exec 'from %s import *' % name
		exec 'import %spath' % name
		exec 'path = %spath' % name
		exec 'del %spath' % name
		try:
			exec 'from %s import _exit' % name
		except ImportError:
			pass
		break
else:
	del name
	raise ImportError, 'no os specific module found'

def execl(file, *args):
	execv(file, args)

def execle(file, *args):
	env = args[-1]
	execve(file, args[:-1], env)

def execlp(file, *args):
	execvp(file, args)

def execvp(file, args):
	if '/' in file:
		execv(file, args)
		return
	ENOENT = 2
	if environ.has_key('PATH'):
		import string
		PATH = string.splitfields(environ['PATH'], ':')
	else:
		PATH = ['', '/bin', '/usr/bin']
	exc, arg = (ENOENT, 'No such file or directory')
	for dir in PATH:
		fullname = path.join(dir, file)
		try:
			execv(fullname, args)
		except error, (errno, msg):
			if errno != ENOENT:
				exc, arg = error, (errno, msg)
	raise exc, arg
