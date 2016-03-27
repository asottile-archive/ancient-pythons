#! /usr/local/bin/python

# WWW server invoked by inetd.
# Stdin and stdout are connected to a TCP/IP socket.
# Serves one request.


# Configuration section
#
DIR = '/ufs/guido/src/www/www-data/'
HOME = '/ufs/guido/src/www'
LOG = HOME + '/Log-inet'


# Imported modules
#
import sys
sys.path.insert(0, HOME)
import time
import os
import socket
import string
import calendar
import wwwlib


# Main program
#
def main():
	try:
		fd = sys.stdin.fileno()
		s = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
		host, port = s.getpeername()
	except:
		host = '???'
	serve(sys.stdin, sys.stdout, host)


# Server routine
#
def serve(input, output, client):
	request = input.readline()
	if request[-1:] == '\n': request = request[:-1]
	if request[-1:] == '\r': request = request[:-1]
	words = string.split(request)
	if len(words) < 2 or string.lower(words[0]) <> 'get':
		log('bad request from', client, `request`[:40])
		return
	addr = words[1]
	scheme, host, port, path, search, anchor = wwwlib.parse_addr(addr)
	if scheme and scheme <> 'http':
		log('request bad scheme from', client, 'in', `addr`)
		output.write('Bad scheme in requested address\n')
		return
	if host and host <> thishost:
		log('request bad host from', client, 'in', `addr`)
		output.write('Non-local host in requested address\n')
		return
	if port and port <> `thisport`:
		log('request bad port from', client, 'in', `addr`)
		output.write('Unexpected host in requested address\n')
		return
	if search:
		log('request with search key from', client, 'in', `addr`)
		output.write('Search key not supported by this server\n')
		return
	while path[:1] == '/': path = path[1:]
	path = os.path.normpath(path)
	if path[:1] == '.':
		log('request illegal path from', client, 'in', `addr`)
		output.write('Illegal path in requested address\n')
		return
	path = DIR + path
	if not os.path.isfile(path):
		log('request non-file path from', client, 'in', `addr`)
		output.write('Invalid path in requested address\n')
		return
	try:
		f = open(path, 'r')
	except IOError, msg:
		log('IOError', str(msg), 'opening', path, 'for', client)
		output.write('Access violation in requested address\n')
		return
	log('sending', path[len(DIR):], 'to', client)
##	if path[-5:] != '.html':
##		log('sending <PLAINTEXT> prefix to', client)
##		output.write('<PLAINTEXT>\n')
	try:
		while 1:
			buf = f.read(8192)
			if not buf: break
			output.write(buf)
	except IOError, msg:
		log('IOError', msg, 'reading', path, 'for', client)


# Write a log message
#
def log(*args):
	now = time.time()
	broken_up_time = time.localtime(now)
	s = calendar.asctime(broken_up_time)[4:]
	for arg in args: s = s + (' ' + arg)
	s = s + '\n'
	f = open(LOG, 'a')
	f.write(s)
	f.close()


main()
