"""Run a subprocess and communicate with it via stdin, stdout, and stderr.

Requires that platform supports, eg, posix-style 'os.pipe' and 'os.fork'
routines.

Subprocess class features:

 - provides non-blocking stdin and stderr reads

 - provides subprocess stop and continue, kill-on-deletion

 - provides (kludgy) detection of subprocess startup failure - see
   implementation notes in the code; suggestions sought!

 - Subprocess objects have nice, informative string rep (as every good object
   ought)."""

__version__ = "1.1"

# subproc.py,v 1.1 1995/03/10 14:43:11 guido Exp
# Originally by ken manheimer, ken.manheimer@nist.gov, jan 1995.

# Prior art: Initially based python code examples demonstrating usage of pipes
#	     and subprocesses, primarily one by jose pereira.

# Implementation notes:
# - I'm not using the fcntl module to implement non-blocking file descriptors,
#   because i don't know what all in it is portable and what is not.  I'm not
#   about to provide for different platform contingencies - at that extent, the
#   effort would be better spent hacking 'expect' into python.
# - Todo? - Incorporate an error-output handler approach, where error output is
#	    checked on regular IO, when a handler is defined, and passed to the
#	    handler (eg for printing) immediately as it shows...
# - Detection of failed subprocess startup is a gross kludge, at present.

# - new additions (1.3, 1.4):
#  - Readbuf, taken from donn cave's iobuf addition, implements non-blocking
#    reads based solely on os.read with select, while capitalizing big-time on
#    multi-char read chunking.
#  - Subproc deletion frees up pipe file descriptors, so they're not exhausted.
#
# ken.manheimer@nist.gov


import sys, os, string, time, types
import select

SubprocessError = 'SubprocessError'
# You may need to increase execvp_grace_seconds, if you have a large or slow
# path to search:
execvp_grace_seconds = 1

class Subprocess:
    """Run and communicate asynchronously with a subprocess.

    Provides non-blocking reads in the form of '.readPendingChars' and
    '.readPendingLine'.

    '.readline' will block until it gets a complete line.

    '.peekPendingChar' does a non-blocking, non-consuming read for pending
    output, and can be used before '.readline' to check non-destructively for
    pending output.  '.waitForPendingChar(timeout, pollPause=.1)' blocks until
    a new character is pending, or timeout secs pass, with granularity of
    pollPause seconds."""

    pid = 0
    cmd = ''
    expire_noisily = 1			# Announce subproc destruction?
    pipefiles = []
    readbuf = 0				# fork will assign to be a readbuf obj
    errbuf = 0				# fork will assign to be a readbuf obj

    def __init__(self, cmd, expire_noisily=0):
	"""Launch a subprocess, given command string COMMAND."""
	self.cmd = cmd
	self.pid = 0
	self.expire_noisily = expire_noisily
	self.fork()

    def fork(self, cmd=None):
	"""Fork a subprocess with designated COMMAND (default, self.cmd)."""
	if cmd: self.cmd = cmd
	else: cmd = self.cmd
	cmd = string.split(self.cmd)
	pRc, cWp = os.pipe()		# parent-read-child, child-write-parent
	cRp, pWc = os.pipe()		# child-read-parent, parent-write-child
	pRe, cWe = os.pipe()		# parent-read-error, child-write-error
	self.pipefiles = [pRc, cWp, cRp, pWc, pRe, cWe]

	self.pid = os.fork()

	if self.pid == 0:	#### CHILD ####
	    parentErr = os.dup(2)	# Preserve handle on *parent's* stderr
	    # Reopen stdin, out, err, on pipe ends:
	    os.dup2(cRp, 0)		# cRp = sys.stdin
	    os.dup2(cWp, 1)		# cWp = sys.stdout
	    os.dup2(cWe, 2)		# cWe = sys.stderr
	    # Ensure (within reason) stray file descriptors are closed:
	    for i in range(4,100):
		if i != parentErr:
		    try: os.close(i)
		    except: pass

	    try:			# Exec the command:
		os.execvp(cmd[0], cmd)					# >*<
		os._exit(1)		# Shouldn't get here		# ***>

	    except:
		os.dup2(parentErr, 2)	# Reconnect to parent's stdout
		sys.stderr.write("**execvp failed, '%s'**\n" %
				 str(sys.exc_value))
		os._exit(1)						# ***>
	    os._exit(1)			# Shouldn't get here.		# ***>

	else:		### PARENT ###
	    # Connect to the child's file descriptors, using our customized
	    # fdopen:
	    self.toChild = pWc
	    self.readbuf = ReadBuf(pRc)
	    self.errbuf = ReadBuf(pRe)
	    time.sleep(execvp_grace_seconds)
	    # The following check is probably very weak.
	    if not self.cont():
		map(os.close, [pRc, cWp, cRp, pWc, pRe, cWe])
		raise SubprocessError, "Subprocess '%s' failed." % self.cmd

    ### Write input to subprocess ###

    def write(self, str):
	"""Write a STRING to the subprocess."""

	if not self.pid:
	    raise SubprocessError, "no child"				# ===>
	else:
	    if select.select([],[self.toChild],[],0)[1] != []:
		os.write(self.toChild, str)
	    else:
		raise IOError, "write to %s blocked" % self		# ===>

    def writeline(self, line=''):
	"""Write STRING, with added newline termination, to subprocess."""
	self.write(line + '\n')

    ### Get output from subprocess ###

    def peekPendingChar(self):
	"""Return, but (effectively) do not consume a single pending output
	char, or return null string if none pending."""

	return self.readbuf.peekPendingChar()				# ===>
    def peekPendingErrChar(self):
	"""Return, but (effectively) do not consume a single pending output
	char, or return null string if none pending."""

	return self.errbuf.peekPendingChar()				# ===>

    def waitForPendingChar(self, timeout, pollPause=.1):
	"""Block max TIMEOUT secs until we peek a pending char, returning the
	char, or '' if none encountered.

	Pause POLLPAUSE secs (default .1) between polls."""

	accume = 0
	while 1:
	    nextChar = self.readbuf.peekPendingChar()
	    if nextChar or (accume > timeout): return nextChar
	    time.sleep(pollPause)
	    accume = accume + pollPause

    def readPendingChars(self):
	"""Read all currently pending subprocess output as a single string."""
	return self.readbuf.readPendingChars()
    def readPendingErrChars(self):
	"""Read all currently pending subprocess error output as a single
	string."""
	return self.errbuf.readPendingChars()				# ===>

    def readPendingLine(self):
	"""Read currently pending subprocess output, up to a complete line
	(newline inclusive)."""
	return self.readbuf.readPendingLine()
    def readPendingErrLine(self):
	"""Read currently pending subprocess error output, up to a complete
	line (newline inclusive)."""
	return self.errbuf.readPendingLine()

    def readline(self):
	"""Return next complete line of subprocess output, blocking until
	then."""
	return self.readbuf.readline()
    def readlineErr(self):
	"""Return next complete line of subprocess error output, blocking until
	then."""
	return self.errbuf.readline()

    ### Subprocess Control ###

    def status(self):
	"""Return string indicating whether process is alive or dead."""
	if not self.cmd:
	    status = 'sans command'
	elif not self.pid:
	    status = 'sans process'
	elif not self.cont():
	    status = "(unresponding) '%s'" % self.cmd
	else:
	    status = "'%s'" % self.cmd
	return status

    def stop(self, verbose=1):
	"""Signal subprocess with STOP (17), returning 'stopped' if ok, or 0
	otherwise."""
	try:
	    os.kill(self.pid, 17)
	    if verbose: print "Stopped '%s'" % self.cmd
	    return 'stopped'
	except os.error:
	    if verbose:
		print "Stop failed for '%s' - '%s'" % (self.cmd, sys.exc_value)
	    return 0
    def cont(self, verbose=0):
	"""Signal subprocess with CONT (19), returning 'continued' if ok, or 0
	otherwise."""
	try:
	    os.kill(self.pid, 19)
	    if verbose: print "Continued '%s'" % self.cmd
	    return 'continued'
	except os.error:
	    if verbose:
		print ("Continue failed for '%s' - '%s'" %
		       (self.cmd, sys.exc_value))
	    return 0

    def die(self):
	"""Send process PID signal SIG (default 9, 'kill'), returning None once
         it is successfully reaped.

	SubprocessError is raised if process is not successfully killed."""

	if not self.pid:
	    raise SubprocessError, "No process"				# ===>
	elif not self.cont():
	    raise SubprocessError, "Can't signal subproc %s" % self	# ===>

	# Try sending first a TERM and then a KILL signal.
	keep_trying = 1
	sigs = [('TERMinated', 15), ('KILLed', 19)]
	for sig in sigs:
	    try:
		os.kill(self.pid, sig[1])
	    except posix.error:
		# keep trying
		pass
	    # Try a couple or three times to reap the process with waitpid:
	    for i in range(5):
		# WNOHANG == 1 on sunos, presumably same elsewhere.
		if os.waitpid(self.pid, 1):
		    if self.expire_noisily:
			print ("\n(%s subproc %d '%s' / %s)" %
			       (sig[0], self.pid, self.cmd,
				hex(id(self))[2:]))
		    for i in self.pipefiles:
			os.close(i)
		    self.pid = 0
		    return None						# ===>
		time.sleep(.1)
	# Only got here if subprocess is not gone:
	raise (SubprocessError,
	       ("Failed kill of subproc %d, '%s', with signals %s" %
		(self.pid, self.cmd, map(lambda(x): x[0], sigs))))
    def __del__(self):
	"""Terminate the subprocess"""
	if self.pid:
	    self.die()
    def __repr__(self):
	status = self.status()
	return '<Subprocess ' + status + ', at ' + hex(id(self))[2:] + '>\n'
    
#############################################################################
#####		      Non-blocking read operations			#####
#############################################################################

class ReadBuf:
    """Output buffer for non-blocking reads on selectable files like pipes and
    sockets.  Init with a file descriptor for the file."""

    def __init__(self, fd, maxChunkSize=1024):
	"""Encapsulate file descriptor FD, with optional MAX_READ_CHUNK_SIZE
	(default 1024)."""

	if fd < 0:
	    raise ValueError
	self.fd = fd
	self.eof = 0			# May be set with stuff still in .buf
	self.buf = ''
	self.chunkSize = maxChunkSize	# Biggest read chunk, default 1024.

    def peekPendingChar(self):
	"""Return, but don't consume, first character of unconsumed output from
	file, or empty string if none."""

	if self.buf:
	    return self.buf[0]						# ===>

	if self.eof:
	    return ''							# ===>

	sel = select.select([self.fd], [], [self.fd], 0)
	if sel[2]:
	    self.eof = 1
	if sel[0]:
	    self.buf = os.read(self.fd, self.chunkSize)			# ===>
	    return self.buf[0]		# Assume select don't lie.
	else: return ''							# ===>
	

    def readPendingChar(self):
	"""Consume first character of unconsumed output from file, or empty
	string if none."""

	if self.buf:
	    got, self.buf = self.buf[0], self.buf[1:]
	    return got							# ===>

	if self.eof:
	    return ''							# ===>

	sel = select.select([self.fd], [], [self.fd], 0)
	if sel[2]:
	    self.eof = 1
	if sel[0]:
	    return os.read(self.fd, 1)					# ===>
	else: return ''							# ===>

    def readPendingChars(self):
	"""Consume uncomsumed output from FILE, or empty string if nothing
	pending."""

	if self.buf:
	    got, self.buf = self.buf, ''
	    return got							# ===>

	if self.eof:
	    return ''							# ===>

	sel = select.select([self.fd], [], [self.fd], 0)
	if sel[2]:
	    self.eof = 1
	if sel[0]:
	    return os.read(self.fd, self.chunkSize)			# ===>
	else: return ''							# ===>

    def readPendingLine(self, block=0):
	"""Return pending output from FILE, up to first newline (inclusive).

	Does not block unless optional arg BLOCK is true.

	Note that an error will be raised if a new eof is encountered without
	any newline."""

	if self.buf:
	    to = string.find(self.buf, '\n')
	    if to != -1:
		got, self.buf = self.buf[0:to+1], self.buf[to+1:]
		return got						# ===>
	    else:
		got, self.buf = self.buf, ''
	else:
	    if self.eof:
		return ''						# ===>
	    else:
		got = ''

	# Herein, 'got' contains the (former) contents of the buffer, and it
	# doesn't include a newline.
	
	while 1:			# (we'll only loop if block set)
	    sel = select.select([self.fd], [], [self.fd], 0)
	    if sel[2]:
		self.eof = 1
	    if sel[0]:
		got = got + os.read(self.fd, self.chunkSize)

	    to = string.find(got, '\n')
	    if to != -1:
		self.buf, got = got[to+1:], got[:to+1]
		return got						# ===>
	    if not block:
		return got						# ===>
	    elif self.eof:
		# Oops.  No newline, and we don't have a complete line.  Rather
		# than blocking forever, we'll buffer what we've read and raise
		# an IOError.  Seems suitable to me...
		self.buf = got
		raise IOError, 'Blocking read for newline hit EOF'
	    # otherwise - no newline, blocking requested, no eof - loop. # ==^

    def readline(self):
	"""Return next output line from file, blocking until it is received."""

	return self.readPendingLine(1)					# ===>


#############################################################################
#####			An example subprocess interfaces		#####
#############################################################################

class Ph:
    """Convenient interface to CCSO 'ph' nameserver subprocess.

    .query('string...') method takes a query and returns a list of dicts, each
    of which represents one entry."""

    # Note that i made this a class that handles a subprocess object, rather
    # than one that inherits from it.  I didn't see any functional
    # disadvantages, and didn't think that full support of the entire
    # Subprocess functionality was in any way suitable for interaction with
    # this specialized interface.  ?  klm 13-Jan-1995

    def __init__(self):
	try:
	    self.proc = Subprocess('ph', 1)
	except:
	    raise SubprocessError, ('failure starting ph: %s' %		# ===>
				    str(sys.exc_value))

    def query(self, q):
	"""Send a query and return a list of dicts for responses.

	Raise a ValueError if ph responds with an error."""

	self.clear()

	self.proc.writeline('query ' + q)
	got = []; it = {}
	while 1:
	    response = self.getreply()	# Should get null on new prompt.
	    if it:
		got.append(it)
		it = {}
	    if not response:
		return got						# ===>
	    elif type(response) == types.StringType:
		raise ValueError, "ph failed match: '%s'" % response	# ===>
	    for line in response:
		# convert to a dict:
		line = string.splitfields(line, ':')
		it[string.strip(line[0])] = (
		    string.strip(string.join(line[1:])))
	
    def getreply(self):
	"""Consume next response from ph, returning list of lines or string
	err."""
	# Key on first char:  (First line may lack newline.)
	#  - dash	discard line
	#  - 'ph> '	conclusion of response
	#  - number	error message
	#  - whitespace	beginning of next response

	nextChar = self.proc.waitForPendingChar(60)
	if not nextChar:
	    raise SubprocessError, 'ph subprocess not responding'	# ===>
	elif nextChar == '-':
	    # dashed line - discard it, and continue reading:
	    self.proc.readline()
	    return self.getreply()					# ===>
	elif nextChar == 'p':
	    # 'ph> ' prompt - don't think we should hit this, but what the hay:
	    return ''							# ===>
	elif nextChar in '0123456789':
	    # Error notice - we're currently assuming single line errors:
	    return self.proc.readline()[:-1]				# ===>
	elif nextChar in ' \t':
	    # Get content, up to next dashed line:
	    got = []
	    while nextChar != '-' and nextChar != '':
		got.append(self.proc.readline()[:-1])
		nextChar = self.proc.peekPendingChar()
	    return got
    def __repr__(self):
	return "<Ph instance, %s at %s>\n" % (self.proc.status(),
					     hex(id(self))[2:])
    def clear(self):
	"""Clear-out initial preface or residual subproc input and output."""
	pause = .5; maxIter = 10	# 5 seconds to clear
	iterations = 0
	got = ''
	self.proc.write('')
	while iterations < maxIter:
	    got = got + self.proc.readPendingChars()
	    # Strip out all but the last incomplete line:
	    got = string.splitfields(got, '\n')[-1]
	    if got == 'ph> ': return	# Ok.				  ===>
	    time.sleep(pause)
	raise SubprocessError, ('ph not responding within %s secs' %
				pause * maxIter)

#############################################################################
#####				  Test					#####
#############################################################################

def test(p=0):
    print "\tOpening subprocess:"
    p = Subprocess('cat', 1)		# set to expire noisily...
    print p
    print "\tOpening bogus subprocess, should fail:"
    try:
	b = Subprocess('/', 1)
	print "\tOops!  Null-named subprocess startup *succeeded*?!?"
    except SubprocessError:
	print "\t...yep, it failed."
    print '\tWrite, then read, two newline-teriminated lines, using readline:'
    p.write('first full line written\n'); p.write('second.\n')
##    p.write('first full line written\nsecond.\n')
    print `p.readline()`
    print `p.readline()`
    print '\tThree lines, last sans newline, read using combination:'
    p.write('first\n'); p.write('second\n'); p.write('third, (no cr)')
    print '\tFirst line via readline:'
    print `p.readline()`
    print '\tRest via readPendingChars:'
    print `p.readPendingChars()`
    print "\tStopping then continuing subprocess (verbose):"
    if not p.stop(1):			# verbose stop
	print '\t** Stop seems to have failed!'
    else:
	print '\tWriting line while subprocess is paused...'
	p.write('written while subprocess paused\n')
	print '\tNonblocking read of paused subprocess (should be empty):'
	print `p.readPendingChars()`
	print '\tContinuing subprocess (verbose):'
	if not p.cont(1):		# verbose continue
	    print '\t** Continue seems to have failed!  Probly lost subproc...'
	    return p
	else:
	    print '\tReading accumulated line, blocking read:'
	    print `p.readline()`
	    print "\tDeleting subproc, which was set to die noisily:"
	    del p
	    print "\tDone."
	    return None

if __name__ == '__main__':
	test()
