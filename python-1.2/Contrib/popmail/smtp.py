# Implements RFC 821 Simple Mail Transport Protocol (SMTP)
#
# See the RFC for what each of these methods should do or
# return
#
# Inherits from MailTransport
#
# mail_message(message) -- MAY OR MAY NOT WORK! NOT FULLY TESTED!
# hello(domain)
# mail_from(address)
# mail_to(address)
# data(mail_message)
# verify(mail_name)
# expand(mail_name)
# reset()
# noop()
#
# For bugs you can send mail to me at jkute@mcs.com

from mailtran import *

hello 	      = 'HELO %s'
mail 	      = 'MAIL FROM:%s'
recipient     = 'RCPT TO:%s'
data 	      = 'DATA'
reset 	      = 'RSET'
send 	      = 'SEND FROM:%s'
send_or_mail  = 'SOML FROM:%s'
send_and_mail = 'SAML FROM:%s'
verify	      = 'VRFY %s'
expand	      = 'EXPN %s'
help	      = 'HELP %s'
noop	      = 'NOOP'
turn	      = 'TURN'

messages = {211: 'System status, or system help reply',
	    214: 'Help message',
	    220: '%s Service ready',
	    221: '%s Service closing transmission channel',
	    250: 'Requested mail action okay, completed',
	    251: 'User not local; will forward to %s',
	    354: 'Start mail input; end with <CRLF>.<CRLF>',
	    421: '%s Service not available, closing transmission channel',
	    450: 'Requested mail action not taken: mailbox unavailable',
	    451: 'Requested action aborted: local error in processing',
	    452: 'Requested action not taken: insufficient system storage',
	    500: 'Syntax error, command unrecognized',
	    501: 'Syntax error in parameters or arguments',
	    502: 'Command not implemented',
	    503: 'Bad sequence of commands',
	    504: 'Command parameter not implemented',
	    550: 'Requested action not taken: mailbox unavailable',
	    551: 'User not local; please try %s',
	    552: 'Requested mail action aborted: exceeded storage allocation',
	    553: 'Requested action not taken: mailbox name not allowed',
	    554: 'Transaction failed'}

class SMTP(MailTransport):
    
    def __init__(self, debug = 0):
	MailTransport.__init__(self, debug)
	self.multiend = regex.compile('^[0-9][0-9][0-9][ ]<.*>.*')
	self.okay = regex.compile('^[23].*\n')
	self.error = regex.compile('^[45].*')
	self.exception = 'SMTPError'
	self.port = 25
	self.log = Log('SMTPlog').log

    def mail_message(self, message):
	if type(message) == type([]):
	    f = StringIO(string.joinfields(message, ''))
	    msg = message
	else:
	    f = StringIO(message)
	    msg = string.splitfields(message, '\n')

	self.hello(gethostname())

	m = Message(f)

	(name, addr) = m.getaddr('from')
	tolist = m.getaddrlist('to')

	self.mail_from(addr)

	for person in tolist:
	    self.mail_to(person[1])

	return self.data(msg)

    def hello(self, domain):
	self.__send__(hello % domain)
	return 	self.__checkerr__(self.__get__())

    def mail_from(self, address):
	self.__send__(mail % address)
	return 	self.__checkerr__(self.__get__())

    def mail_to(self, address):
	self.__send__(recipient % address)
	return 	self.__checkerr__(self.__get__())

    def data(self, message):
	textlist = []
	if type(message) != type([]):
	    raise TypeError, "message must be a list of strings"

	for line in message:
	    if regex.match('^\..*', line) >= 0 and \
	       line != message[len(message)-1]:
		newline = '.' + line
	    else:
		newline = line
	    textlist.append(newline)

	textlist.append('.\r\n')

	self.__send__(data)
	self.__checkerr__(self.__get__())
	self.__send__(string.joinfields(textlist, ''), 2)
	return 	self.__checkerr__(self.__get__())

    def verify(self, name):
	addresses = []
	self.__send__(verify % name)
	names = self.__get__(0, MULTILINE)
	for name in names:
	    (user, address) = parseaddr(name[4:])
	    addresses.append(address)
	return addresses

    def expand(self, name):
	addresses = []
	self.__send__(expand % name)
	names = self.__get__(0, MULTILINE)
	for name in names:
	    (user, address) = parseaddr(name[4:])
	    addresses.append(address)
	return addresses

    def reset(self):
	self.__send__(reset)
	return 	self.__checkerr__(self.__get__())

    def noop(self):
	self.__send__(noop)
	return 	self.__checkerr__(self.__get__())
