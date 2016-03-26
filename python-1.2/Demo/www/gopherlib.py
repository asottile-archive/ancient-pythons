# Gopher protocol interface

# Default selector, host and port
DEF_SELECTOR = ''
DEF_HOST     = 'gopher.micro.umn.edu'
DEF_PORT     = 70

# Recognized file types (same names as in Gopher C source)
A_FILE       = '0'
A_DIRECTORY  = '1'
A_CSO        = '2'
A_ERROR      = '3'
A_MACHEX     = '4'
A_PCHEX      = '5'
A_INDEX      = '7'
A_TELNET     = '8'
A_UNIXBIN    = '9'
A_SOUND      = 's'
A_EVENT      = 'e'
A_CALENDAR   = 'c'
A_HTML       = 'h'
A_TN3270     = 'T'
A_MIME       = 'M'
A_IMAGE      = 'I'
A_EOI        = '.'

# These are unofficial ones that I've encountered...
a_WHOIS      = 'w'
a_QUERY      = 'q'
a_GIF        = 'g'
a_BUT        = 'b' # What's this?


# Dictionary mapping known file types to strings
_type_to_name_map = { \
	A_FILE: 'TEXT', \
	A_DIRECTORY: 'DIR', \
	A_CSO: 'CSO', \
	A_ERROR: 'ERROR', \
	A_MACHEX: 'BINHEX', \
	A_PCHEX: 'DOS', \
	A_INDEX: 'INDEX', \
	A_TELNET: 'TELNET', \
	A_UNIXBIN: 'BINARY', \
	A_SOUND: 'SOUND', \
	A_EVENT: 'EVENT', \
	A_CALENDAR: 'CALENDAR', \
	A_HTML: 'HTML', \
	A_TN3270: 'TN3270', \
	A_MIME: 'MIME', \
	}

# Function mapping all file types to strings; unknown types become TYPE='x'
def type_to_name(gtype):
	if _type_to_name_map.has_key(gtype):
		return _type_to_name_map[gtype]
	return 'TYPE=' + `gtype`

# Names for characters and strings
CRLF = '\r\n'
TAB = '\t'

# Send a selector to a given host and port, return a file with the reply
def send_selector(selector, host, port):
	import socket
	if not port:
		port = DEF_PORT
	elif type(port) == type(''):
		import string
		port = string.atoi(port)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	s.send(selector + CRLF)
	s.shutdown(1)
	return s.makefile('r')

# The following functions interpret the data returned by the gopher
# server according to the expected type, e.g. textfile or directory

# Get a directory in the form of a list of entries
def get_directory(f):
	import string
	list = []
	while 1:
		line = f.readline()
		if not line:
			print '(Unexpected EOF from server)'
			break
		if line[-2:] == CRLF:
			line = line[:-2]
		elif line[-1:] in CRLF:
			line = line[:-1]
		if line == '.':
			break
		if not line:
			print '(Empty line from server)'
			continue
		gtype = line[0]
		parts = string.splitfields(line[1:], TAB)
		if len(parts) < 4:
			print '(Bad line from server:', `line`, ')'
			continue
		if len(parts) > 4:
			print '(Extra info from server:', parts[4:], ')'
		parts.insert(0, gtype)
		list.append(parts)
	return list

# Get a text file as a list of lines, with trailing CRLF stripped
def get_textfile(f):
	list = []
	get_alt_textfile(f, list.append)
	return list

# Get a text file and pass each line to a function, with trailing CRLF stripped
def get_alt_textfile(f, func):
	while 1:
		line = f.readline()
		if not line:
			print '(Unexpected EOF from server)'
			break
		if line[-2:] == CRLF:
			line = line[:-2]
		elif line[-1:] in CRLF:
			line = line[:-1]
		if line == '.':
			break
		if line[:2] == '..':
			line = line[1:]
		func(line)

# Get a binary file as one solid data block
def get_binary(f):
	data = f.read()
	return data

# Get a binary file and pass each block to a function
def get_alt_binary(f, func, blocksize):
	while 1:
		data = f.read(blocksize)
		if not data:
			break
		func(data)

# Trivial test program
def test():
	import sys
	selector, host, port = sys.argv[1], sys.argv[2], sys.argv[3]
	f = send_selector(selector, host, port)
	list = get_directory(f)
	f.close()
	for item in list:
		print item
