import os
import time
import string
import socket
import select

error = 'helplib.error' # Exception

HELP_PORT = 4000
HELP_SERVER = '/ufs/guido/bin/wwww -s &'
STARTUP_DELAY = 5
PING_TIMEOUT = 5

help_wname = None
help_host = None
help_port = None

def init(wname):
	global help_wname, help_host, help_port
	help_wname = wname
	help_port = HELP_PORT
	#
	if os.environ.has_key('DISPLAY'):
		display = os.environ['DISPLAY']
	else:
		display = ':0'
	#
	if ':' in display:
		i = string.index(display, ':')
	else:
		i = len(display)
	#
	thishost = socket.gethostname()
	#
	help_host = display[:i]
	if help_host == 'unix' or help_host == '':
		help_host = thishost
	#
	if not ping():
		if socket.gethostbyname(help_host) <> \
			  socket.gethostbyname(thishost):
			raise error, 'Won\'t start remote help server'
		print 'helplib.init: Starting help server...'
		sts = os.system(HELP_SERVER)
		if sts: raise error, \
				'Exit status ' + `sts` + ' from help server'
		time.sleep(STARTUP_DELAY)


def ping():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	msg = help_wname + ' echo'
	s.sendto(msg, (help_host, help_port))
	result = select.select([s], [], [], PING_TIMEOUT)
	if not result:
		print 'helplib.ping: No select result'
		return 0
	rlist, wlist, xlist = result
	if s in rlist:
		try:
			data = s.recv(100)
		except socket.error, msg:
			print 'helplib.ping: Socket error:', msg
			return 0
		print 'helplib.ping: Echo data:', `data`
		return 1
	print 'helplib.ping: Timeout'
	return 0


def show(page):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	msg = help_wname + ' goto ' + page
	s.sendto(msg, (help_host, help_port))


def test():
	import sys
	init('1')
	if sys.argv[1:]: show(sys.argv[1])
	else: show('http://voorn.cwi.nl/default.html')
