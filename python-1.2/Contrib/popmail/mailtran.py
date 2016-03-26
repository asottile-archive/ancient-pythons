# A MailTransport class providing common methods used by pop3 and smtp
#
# This class is only useful if you are doing some type of telnet-based
# mail service.
#
# There are two useful methods in this class, and two more if you are
# writing a subclass.
#
# For general use there are:
#
# open_server(hostname)
# close()
#
# If you are writing a subclass, you can use:
#
# __get__(size_of_buffer, is_multiline, debug_level)
# __send__(command, debug_level)
# __checkerr__(expected_response, exception_to_raise, debug_level)
#
# See the pop.py example and the libraries pop3.py and smtp.py for
# examples of how to use these methods
#
# For bugs you can send mail to me at jkute@mcs.com

import sys, posix, time, regex, string, os
from regex_syntax import *
from socket import *
from StringIO import *
from rfc822 import *
from lockfile import *

servname = 'telnet'

MULTILINE = 1

regex.set_syntax(RE_NO_BK_PARENS | RE_NO_BK_VBAR | RE_CONTEXT_INDEP_OPS)
isnum = regex.compile('[0-9]*')

class MailTransport:
    def __init__(self, debug = 0):
	self.s = socket(AF_INET, SOCK_STREAM)
	self.f = self.s.makefile('r')
	self.multiend = regex.compile('^\.\r\n')
	self.okay = regex.compile('^\+OK.*')
	self.error = regex.compile('^\-ERR.*')
	self.log = Log('mtranlog').log
	self.port = 7
	self.debug = debug
	self.exception = 'MailTransportError'

    def open_server(self, host):
	try:
	    hostaddr = gethostbyname(host)
	except error:
	    sys.stderr.write(sys.argv[1] + ': bad host name\n')
	    sys.exit(2)
	#
	try:
	    self.s.connect(host, self.port)
	except error, msg:
	    sys.stderr.write('connect failed: ' + `msg` + '\n')
	    sys.exit(1)

	self.__get__()

    def close(self):
	self.__send__('QUIT')
	self.__get__()
	
    def __get__(self, size = 0, multiline = 0, debug_level = 2):
	list = []
	currsize = 0
	skip = 0

	if not multiline and not size:
	    line = self.f.readline()
	    list.append(line)
	else:
	    while 1:
		line = self.f.readline()

		if not line: break

		if size and not skip:
		    currsize = currsize + len(line)
		    if currsize >= size: 
			list.append(line)
			skip = 1
			continue

		if multiline and self.multiend.match(line) >= 0: 
		    if size and currsize >= size or not size: 
			list.append(line)
			break

		if not skip: list.append(line)

	if self.error.match(list[0]) >= 0 or debug_level <= self.debug:
	    self.log(string.joinfields(list, ''))
	return list

    def __send__(self, cmd, debug_level = 1):
	line = cmd + '\n'
	if debug_level <= self.debug:
	    self.log(line)
	self.s.send(line)

    def __checkerr__(self, response, exception = 'MailTranError', debug_level = 0):
	if self.error.match(response[0]) >= 0:
	    if debug_level <= self.debug:
		self.log(response[0])
	    raise exception, response[0]
	else:
	    return response

# LOGDIR = '/usr/spool/mqueue/'
LOGDIR = '/tmp/'
class Log:
    def __init__(self, logfile):
	try:
	    self.f = open(LOGDIR + logfile, 'a+', 0)
	except IOError:
	    try:
		self.f = open(LOGDIR + logfile, 'w+', 0)
	    except IOError:
		self.f = open(LOGDIR + logfile, 'w', 0)

	self.ident = '['+sys.argv[0]+ ':' + repr(posix.getpid()) +']: '
	pass
    def __del__(self):
	self.f.close()
	pass
    def log(self, line):
	self.f.write(self.ident + line)
	self.f.flush()
	
def addtodict(dict, list):
    if len(list) == 2 and isnum.match(list[0]) and isnum.match(list[1]):
	num = eval(list[0])
	size = eval(list[1])
	dict[num] = size
