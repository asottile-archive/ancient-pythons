#! /usr/local/bin/python

# Absolutely minimal WWW server
# Usage: wwwserver [directory [port]]
# Default directory is '.', default port is 2784.
# Logging of connections and requests is done to stdout
# Unexpected server crashes may write their stack trace etc. to stderr

import sys
import time
import os
import string
import getopt
import socket
import time
import calendar
import wwwlib

DEF_PORT = 2784
DEF_DIR = '.'

thishost = socket.gethostname()
thisport = None
thisdir = None

def main():
	global thisport, thisdir
	log('started')
	opts, args = getopt.getopt(sys.argv[1:], '')
	if len(args) > 2:
		print 'usage: wwwserver [port [directory]]'
		sys.exit(2)
	#
	if len(args) > 0:
		thisdir = args[0]
	else:
		thisdir = DEF_DIR
	if thisdir[-1:] <> '/':
		thisdir = thisdir + '/'
	if not os.path.isdir(thisdir):
		print thisdir, ': not a directory'
		sys.exit(2)
	#
	if len(args) > 1:
		thisport = string.atoi(args[1])
	else:
		thisport = DEF_PORT
	#
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind('', thisport)
	s.listen(0)
	sys.exitfunc = lastwish
	#
	log('ready for requests on port', thisport, 'for directory', thisdir)
	#
	while 1:
		log('waiting for next request')
		conn, (client, port) = s.accept()
		serve(conn, client)
		log('closing connection to', client)
		conn.close()
		del conn


def serve(s, client):
	log('connection from', client)
	request = s.recv(1024)
	key = request[:4]
	if string.lower(key) <> 'get ':
		log('bad request from', client, `request`[:40])
		return
	if request[-1:] == '\n': request = request[:-1]
	if request[-1:] == '\r': request = request[:-1]
	addr = string.strip(request[4:])
	scheme, host, port, path, search, anchor = wwwlib.parse_addr(addr)
	if scheme and scheme <> 'http':
		log('request bad scheme from', client, 'in', `addr`)
		s.send('Bad scheme in requested address\n')
		return
	if host and host <> thishost:
		log('request bad host from', client, 'in', `addr`)
		s.send('Non-local host in requested address\n')
		return
	if port and port <> `thisport`:
		log('request bad port from', client, 'in', `addr`)
		s.send('Unexpected host in requested address\n')
		return
	if search:
		log('request with search key from', client, 'in', `addr`)
		s.send('Search key not supported by this server\n')
		return
	while path[:1] == '/': path = path[1:]
	path = os.path.normpath(path)
	if path[:1] == '.':
		log('request illegal path from', client, 'in', `addr`)
		s.send('Illegal path in requested address\n')
		return
	path = thisdir + path
	if not os.path.isfile(path):
		log('request non-file path from', client, 'in', `addr`)
		s.send('Invalid path in requested address\n')
		return
	try:
		f = open(path, 'r')
	except IOError, msg:
		log('IOError', msg, 'opening', path, 'for', client)
		s.send('Access violation in requested address\n')
		return
	log('sending', path[len(thisdir):], 'to', client)
	sf = s.makefile('w')
	if path[-5:] != '.html':
		log('sending <PLAINTEXT> prefix to', client)
		sf.write('<PLAINTEXT>\n')
	try:
		while 1:
			buf = f.read(8192)
			if not buf: break
			sf.write(buf)
	except IOError, msg:
		log('IOError', msg, 'reading', path, 'for', client)
	f.close()
	sf.close()


def lastwish():
	log('killed')


def log(*args):
	now = time.time()
	broken_up_time = time.localtime(now)[:-1] # Strip trailing what?
	print calendar.asctime(broken_up_time)[4:],
	for arg in args: print arg,
	print
	sys.stdout.flush()


main()
