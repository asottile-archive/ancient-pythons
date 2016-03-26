# Implements RFC 1460 POP3 Mail Service
#
# See the RFC for what each of these methods should do or
# return
#
# Inherits from MailTransport
#
# login(name, password)
# status()
# list(message_num) -- message num is optional
# retrieve(message_num)
# delete(message_num)
# reset()
# last()
# noop()
#
# For bugs you can send mail to me at jkute@mcs.com

from mailtran import *

user 	 = 'USER %s'
password = 'PASS %s'
status   = 'STAT'
list	 = 'LIST'
retrieve = 'RETR %s'
delete	 = 'DELE %s'
noop	 = 'NOOP'
reset	 = 'RSET'
last	 = 'LAST'

class POP3(MailTransport):

    def __init__(self, debug = 0):
	MailTransport.__init__(self, debug)
	self.multiend = regex.compile('^\.\r\n.*')
	self.okay = regex.compile('^\+OK.*')
	self.error = regex.compile('^\-ERR.*')
	self.log = Log('POP3log').log
	self.port = 110
	self.exception = 'POP3Error'

    def login(self, name, pw):
	self.__send__(user % name)
	self.__checkerr__(self.__get__())
	self.__send__(password % pw, 3)
	self.__checkerr__(self.__get__())

    def status(self):
	self.__send__(status)
	statlist = self.__checkerr__(self.__get__())
	stats = string.split(statlist[0])
	num = stats[1]
	size = stats[2]
	return (num, size)

    def list(self, msgnum = 0):
	msgdict = {}
	if msgnum > 0:
	    self.__send__(list +' %d' % msgnum)
	    listinfo = self.__get__()
	    self.__checkerr__(listinfo)
	else:
	    self.__send__(list)
	    listinfo = self.__get__(0, MULTILINE)

	if self.okay.match(listinfo[0]) >= 0:
	    if msgnum > 0:
		words = string.split(listinfo[0])
		del words[0]
		addtodict(msgdict, words)
	    else:
		del listinfo[0]
		for msg in listinfo:
		    words = string.split(msg)
		    addtodict(msgdict, words)
	return msgdict
	
    def retrieve(self, msgnum):
	msginfo = self.list(msgnum)
	self.__send__(retrieve % msgnum)
	self.__checkerr__(self.__get__())
	if not msginfo.has_key(msgnum):
	    self.log('size information for message %d unavailable\n' % msgnum)
	    return None
	data = self.__get__(msginfo[msgnum], MULTILINE)
	if self.multiend.match(data[len(data)-1]):
	    del data[len(data)-1]
	return data

    def delete(self, msgnum):
	self.__send__(delete % msgnum)
	return 	self.__checkerr__(self.__get__())

    def reset(self):
	self.__send__(reset)
	return 	self.__checkerr__(self.__get__())

    def last(self):
	self.__send__(last)
	return 	self.__checkerr__(self.__get__())

    def noop(self):
	self.__send__(noop)
	return 	self.__checkerr__(self.__get__())
