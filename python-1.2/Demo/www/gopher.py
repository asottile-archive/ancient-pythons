#! /usr/local/bin/python

# A *very* simple interactive gopher client
#
# Usage: gopher [ [selector] host [port] ]

import string
import sys
import os
import socket
from gopherlib import *

# Browser main command, has default arguments
def browser(*args):
	selector = DEF_SELECTOR
	host = DEF_HOST
	port = DEF_PORT
	n = len(args)
	if n > 0 and args[0]:
		selector = args[0]
	if n > 1 and args[1]:
		host = args[1]
	if n > 2 and args[2]:
		port = args[2]
	if n > 3:
		raise RuntimeError, 'too many args'
	try:
		browse_directory('*** TOPLEVEL ***', selector, host, port)
	except socket.error, msg:
		print 'Socket error:', msg
		sys.exit(1)
	except KeyboardInterrupt:
		print '\n[Goodbye]'

# Browse a directory
def browse_directory(description, selector, host, port):
	list = get_directory(send_selector(selector, host, port))
	while 1:
		print '----- MENU:', description, '-----'
		print 'Selector:', `selector`
		print 'Host:', host, ' Port:', port
		print
		for i in range(len(list)):
			item = list[i]
			gtype, descr = item[0], item[1]
			print string.rjust(`i+1`, 3) + ':', descr, \
				'<' + type_to_name(gtype) + '>'
		print
		while 1:
			try:
				str = raw_input('Choice [CR == up a level]: ')
			except EOFError:
				print
				return
			if not str:
				return
			try:
				choice = string.atoi(str)
			except string.atoi_error:
				print 'Choice must be a number; try again:'
				continue
			if not 0 < choice <= len(list):
				print 'Choice out of range; try again:'
				continue
			break
		item = list[choice-1]
		[gtype, i_descr, i_sel, i_host, i_port] = item[:5]
		if typebrowser.has_key(gtype):
			browserfunc = typebrowser[gtype]
		else:
			print 'Unsupported file type', `gtype`, '--> binary'
			browserfunc = browse_binary
		try:
			browserfunc(i_descr, i_sel, i_host, i_port)
		except (IOError, socket.error):
			print '***', sys.exc_type, ':', sys.exc_value

# Browse a text file
def browse_textfile(description, selector, host, port):
	print '----- TEXTFILE:', description, '-----'
	print 'Selector:', `selector`
	print 'Host:', host, ' Port:', port
	print
	cf = send_selector(selector, host, port)
	x = None
	try:
		p = os.popen('${PAGER-more}', 'w')
		x = SaveLines(p)
		get_alt_textfile(cf, x.writeln)
	except IOError, msg:
		print 'IOError:', msg
	if x:
		x.close()
	f = open_savefile()
	if not f:
		return
	cf = send_selector(selector, host, port)
	x = SaveLines(f)
	try:
		get_alt_textfile(cf, x.writeln)
		print 'Done.'
	except IOError, msg:
		print 'IOError:', msg
	x.close()

# Browse a search index
def browse_index(description, selector, host, port):
	while 1:
		print '----- SEARCH:', description, '-----'
		print 'Selector:', `selector`
		print 'Host:', host, ' Port:', port
		print
		try:
			query = raw_input('Query [CR == up a level]: ')
		except EOFError:
			print
			break
		query = string.strip(query)
		if not query:
			break
		if '\t' in query:
			print 'Sorry, queries cannot contain tabs'
			continue
		browse_directory('Search outcome', \
			selector + TAB + query, host, port)

# "Browse" telnet-based information, i.e. open a telnet session
def browse_telnet(description, selector, host, port):
	cmd = 'telnet'
	if selector:
		cmd = cmd + ' -l ' + selector
	cmd = cmd + ' ' + host
	if port:
		cmd = cmd + ' ' + port
	print '----- EXEC:', cmd, '-----'
	sts = os.system(cmd)
	if sts:
		print 'Exit status:', sts

# "Browse" a binary file, i.e. save it to a file
def browse_binary(description, selector, host, port):
	print '----- BINARY:', description, '-----'
	print 'Selector:', `selector`
	print 'Host:', host, ' Port:', port
	print
	f = open_savefile()
	if not f:
		return
	cf = send_selector(selector, host, port)
	x = SaveWithProgress(f)
	get_alt_binary(cf, x.write, 8*1024)
	x.close()

# "Browse" a sound file, i.e. play it or save it
def browse_sound(description, selector, host, port):
	print '----- SOUND:', description, '-----'
	print 'Selector:', `selector`
	print 'Host:', host, ' Port:', port
	print
	f = open_savefile() # Use |playulaw, for instance
	if not f:
		return
	cf = send_selector(selector, host, port)
	x = SaveWithProgress(f)
	get_alt_binary(cf, x.write, 8000) # Exactly 8000 bytes/sec!
	x.close()

# Deny browsing an entry
def browse_not(description, selector, host, port):
	print '----- DENIED:', description, '-----'
	print 'It would be unwise to connect to host', host, 'and port', port
	print 'since the type of connection does not yield a file.'

# Dictionary mapping types to browser functions
typebrowser = { \
	A_FILE: browse_textfile, \
	A_DIRECTORY: browse_directory, \
	A_INDEX: browse_index, \
	A_TELNET: browse_telnet, \
	A_UNIXBIN: browse_binary, \
	A_SOUND: browse_sound, \
	A_TN3270: browse_not, \
	'Z': browse_directory, \
	}

# Class used to save lines, appending a newline to each line
class SaveLines:
	def __init__(self, f):
		self.f = f
	def writeln(self, line):
		self.f.write(line + '\n')
	def close(self):
		sts = self.f.close()
		if sts:
			print 'Exit status:', sts

# Class used to save data while showing progress
class SaveWithProgress:
	def __init__(self, f):
		self.f = f
	def write(self, data):
		sys.stdout.write('#')
		sys.stdout.flush()
		self.f.write(data)
	def close(self):
		print
		sts = self.f.close()
		if sts:
			print 'Exit status:', sts

# Ask for and open a save file, or return None if not to save
def open_savefile():
	try:
		savefile = raw_input( \
	    'Save as file [CR == don\'t save; |pipeline or ~user/... OK]: ')
	except EOFError:
		print
		return None
	savefile = string.strip(savefile)
	if not savefile:
		return None
	if savefile[0] == '|':
		cmd = string.strip(savefile[1:])
		try:
			p = os.popen(cmd, 'w')
		except IOError, msg:
			print `cmd`, ':', msg
			return None
		print 'Piping through', `cmd`, '...'
		return p
	if savefile[0] == '~':
		savefile = os.path.expanduser(savefile)
	try:
		f = open(savefile, 'w')
	except IOError, msg:
		print `savefile`, ':', msg
		return None
	print 'Saving to', `savefile`, '...'
	return f

# Main program
def main():
	if sys.argv[4:]:
		print 'usage: gopher [ [selector] host [port] ]'
		sys.exit(2)
	elif sys.argv[3:]:
		browser(sys.argv[1], sys.argv[2], sys.argv[3])
	elif sys.argv[2:]:
		try:
			port = string.atoi(sys.argv[2])
			selector = ''
			host = sys.argv[1]
		except string.atoi_error:
			selector = sys.argv[1]
			host = sys.argv[2]
			port = ''
		browser(selector, host, port)
	elif sys.argv[1:]:
		browser('', sys.argv[1])
	else:
		browser()

# Call the test program as a main program
main()
