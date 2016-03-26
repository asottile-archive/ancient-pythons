# Collect a list of all the Gopher directories in the world.
# Interrupt the program at any moment to stop, restart it later and it
# will continue where it left off.

import sys
import os
import socket
import marshal
import dbm
from gopherlib import *

KNOWN = '/usr/tmp/@known-gophers'
TODO = '/usr/tmp/@todo-gophers'
TODO_TMP = TODO + '#'
TODO_OLD = TODO + '~'

ROOT = [A_DIRECTORY, 'Root', DEF_SELECTOR, DEF_HOST, DEF_PORT]

def main():
	global known, todo
	known = dbm.open(KNOWN, 'rw', 0666)
	print len(known.keys()), 'entries known'
	try:
		todo = marshal.load(open(TODO, 'r'))
		print len(todo), 'entries to do'
	except IOError:
		print 'IOError on todo, start fresh'
		todo = [ROOT]
	for i in range(1, len(sys.argv)): del todo[0]
	i = 0
	while todo:
		collect(todo[0])
		sys.stdout.flush()
		del todo[0]
		i = i+1
		if i%10 != 0: continue
		sys.stderr.write('Dumping ... ')
		f = open(TODO_TMP, 'w')
		marshal.dump(todo, f)
		f.close()
		##try: os.unlink(TODO_OLD)
		##except os.error: pass
		try: os.rename(TODO, TODO_OLD)
		except os.error: pass
		os.rename(TODO_TMP, TODO)
		sys.stderr.write('done.\n')

def collect(entry):
	print entry
	[selector, host, port] = entry[2:5]
	key = `selector, host, port`
	if known.has_key(key):
		print '*** already seen', known[key]
		return
	try:
		f = send_selector(selector, host, port)
		list = get_directory(f)
		f.close()
	except (IOError, socket.error), msg:
		print '*** error:', msg
		if type(msg) <> type(''):
			msg = `msg`
		known[key] = msg
		return
	print 'Got', len(list), 'subentries'
	for subentry in list:
		gtype = subentry[0]
		if gtype == A_DIRECTORY:
			[s, h, p] = subentry[2:5]
			subkey = `s, h, p`
			if not known.has_key(subkey):
				todo.append(subentry)
		elif not '0' <= gtype <= '9':
			print 'Special type:', subentry
	known[key] = '' # This server is OK

main()
