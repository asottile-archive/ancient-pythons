# WWW protocol interface

# Default home page
WWW_HOME = 'http://info.cern.ch:80/default.html'

# Exception raised when an address leads nowhere
BadAddress = 'wwwlib.BadAddress'

# Parse an "anchoraddr", return (scheme, host, port, path, search, anchor)
#
# Note that search and anchor *include* the leading '?' or '#',
# but host and port don't include the leading '//' or ':' and scheme
# excludes the trailing ':'.
#
# (Some address forms don't support all parts, and some have
# additional parts; yet this does something useful for all formats.)
#
import regex
schemeprog = regex.compile('^[^/:?#]*:')
hostportprog = regex.compile('//[^/:?#]*\(:[0-9]*\)?')
portprog = regex.compile(':[0-9]*')
searchprog = regex.compile('\?[^#]*')
anchorprog = regex.compile('#.*')
#
def parse_addr(anchoraddr):
	i = anchorprog.search(anchoraddr)
	if i >= 0:
		anchor = anchoraddr[i:]
		docaddr = anchoraddr[:i]
	else:
		anchor = ''
		docaddr = anchoraddr
	#
	i = schemeprog.match(docaddr)
	if i >= 0:
		scheme = docaddr[:i-1]
		path = docaddr[i:]
	else:
		scheme = ''
		path = docaddr
	#
	if path[:2] == '//':
		i = hostportprog.match(path)
		hostport = path[2:i]
		path = path[i:]
	else:
		hostport = ''
	#
	i = portprog.search(hostport)
	if i >= 0:
		host = hostport[:i]
		port = hostport[i+1:]
	else:
		host = hostport
		port = ''
	#
	i = searchprog.search(path)
	if i >= 0:
		search = path[i:]
		path = path[:i]
	else:
		search = ''
	#
	return scheme, host, port, path, search, anchor

# Convert a (scheme, ..., anchor) tuple back into an address string
def unparse_addr(scheme, host, port, path, search, anchor):
	a = ''
	if scheme:
		a = a + scheme + ':'
	if host or port:
		a = a + '//' + host
		if port:
			a = a + ':' + port
		if path and path[0] <> '/':
			a = a + '/'
	a = a + path
	if search:
		if search[0] <> '?':
			search = '?' + search
		a = a + search
	if anchor:
		if anchor[0] <> '#':
			anchor = '#' + anchor
		a = a + anchor
	return a

# Turn a relative address into a full address given the parent's address
def full_addr(parent, addr, *isindex):
	pscheme, phost, pport, ppath, psearch, panchor = parse_addr(parent)
	if not pscheme: pscheme = 'file'
	if phost[-1:] == '.': phost = phost[:-1]
	if pscheme == 'http' and pport in ('80', '2784') or pscheme == 'file':
		pport = '' # XXX
	scheme, host, port, path, search, anchor = parse_addr(addr)
	if not scheme: scheme = pscheme
	if scheme == pscheme:
		if not host:
			host = phost
			if not port: port = pport
		if host[-1:] == '.':
			host = host[:-1]
		if not path:
			path = ppath
		elif path[0] <> '/' and '/' in ppath:
			import posixpath
			i = len(ppath)
			while i > 0 and ppath[i-1] <> '/':
				i = i-1
			path = ppath[:i] + path
			path = posixpath.normpath(path)
	if scheme == 'http' and port in ('80', '2784'): port = '' # XXX
	full = unparse_addr(scheme, host, port, path, search, anchor)
	return full

# Get a document, given its (full) address
# (XXX This doesn't support the full range of address schemes yet,
# and of course the "telnet" scheme needs special treatment anyway.)
def get_document(addr):
	scheme, host, port, path, search, anchor = parse_addr(addr)
	#
	if scheme == 'http':
		import httplib, socket, string
		if port:
			try:
				port = string.atoi(port)
			except string.atoi_error:
				raise BadAddress, 'bad port number'
		if search:
			if search[0] <> '?':
				search = '?' + search
			path = path + search
		try:
			data = httplib.get_htmlfile(host, port, path)
		except socket.error, msg:
			if type(msg) <> type(''): msg = `msg`
			raise BadAddress, msg
		# Interpret a short single-line document with no tags
		# as an error message
		if len(data) <= 100 and '<' not in data and \
			'\n' not in data[:-1]:
			if data[-2:] == '\r\n': data = data[:-2]
			elif data[-1:] == '\n': data = data[:-1]
			raise BadAddress, data
		return data
	#
	if (scheme == 'file' or scheme == 'ftp' or scheme == ''):
		import socket
		isdir =  0
		if host <> '' and socket.gethostbyname(host) <> \
			         socket.gethostbyname(socket.gethostname()):
			import ftplib
			class C:
				def add(self, x):
					self.data = self.data + (x + '\n')
			x = C()
			x.data = ''
			try:
				ftp = ftplib.FTP(host)
			except ftplib.all_errors:
				raise BadAddress, \
					'ftp connect to ' + host + ' failed'
			try:
				ftp.login() # user anonymous, passwd user@host
			except ftplib.all_errors:
				raise BadAddress, \
					'ftp login on ' + host + ' failed'
			# First try retrieving as a file, then listing
			# as a directory
			try:
				ftp.retrlines('RETR ' + path, x.add)
				data = x.data
			except ftplib.error_perm:
				try:
					ftp.voidcmd('CWD ' + path)
					names = ftp.nlst()
				except ftplib.all_errors:
					raise BadAddress, \
						'ftp can\'t find ' + path + \
						' on ' + host
				data = names_to_html(host, path, names, 0)
				isdir = 1
			except ftplib.all_errors:
				raise BadAddress, \
					'ftp retrieve ' + path + ' from ' + \
					host + ' failed'
		else:
			import os
			if os.path.isdir(path):
				names = os.listdir(path)
				if os.curdir in names: names.remove(os.curdir)
				if os.pardir in names: names.remove(os.pardir)
				data = names_to_html(host, path, names, 1)
				isdir = 1
			else:
				try:
					data = open(path, 'r').read()
				except IOError, msg:
					raise BadAddress, \
						  'can\'t open local file ' + \
						  `path` + ' : ' + `msg`
		if not isdir and path[-5:] <> '.html':
			data = '<PLAINTEXT>\n' + data
		return data
	#
	if scheme == 'gopher':
		import string
		import gopherlib
		if len(path) >= 2 and path[0] == '/':
			gtype = path[1]
			selector = path[2:]
		else:
			selector = ''
			gtype = gopherlib.A_DIRECTORY
		# Convert '%' escapes in selectors
		while '%' in selector:
			i = string.index(selector, '%')
			xx = selector[i+1:i+3]
			try:
				n = eval('0x' + xx)
				c = chr(n)
			except:
				c = ''
			selector = selector[:i] + c + selector[i+3:]
		if gtype == gopherlib.A_FILE:
			f = gopherlib.send_selector(selector, host, port)
			lines = gopherlib.get_textfile(f)
			lines.append('')
			data = string.joinfields(lines, '\n')
			return '<PLAINTEXT>\n' + data
		if gtype == gopherlib.A_DIRECTORY:
			f = gopherlib.send_selector(selector, host, port)
			directory = gopherlib.get_directory(f)
			return gopher_to_html(directory)
		if gtype == gopherlib.A_HTML:
			f = gopherlib.send_selector(selector, host, port)
			lines = gopherlib.get_textfile(f)
			lines.append('')
			data = string.joinfields(lines, '\n')
			return data
		if gtype == gopherlib.A_INDEX:
			if not search:
				return '<ISINDEX>\n' + \
				       '<TITLE>Gopher index</TITLE>\n' + \
				       '<H1>Enter search keywords</H1>\n'
			words = string.splitfields(search, '+')
			selector = selector + '\t' + string.join(words)
			f = gopherlib.send_selector(selector, host, port)
			directory = gopherlib.get_directory(f)
			return gopher_to_html(directory)
		raise BadAddress, 'unsupported gopher type ' + `gtype`
	#
	raise BadAddress, 'unsupported scheme ' + `scheme`

# Convert a Gopher directory to HTML
def gopher_to_html(directory):
	import string
	import gopherlib
	data = '<TITLE>Gopher menu</TITLE>\n<H1>Gopher menu</H1>\n<UL>\n'
	for item in directory:
		[gtype, userstring, selector, host, port] = item[:5]
		if gtype == gopherlib.A_ERROR:
			text = '<LI>' + userstring + '\n'
		else:
			# Convert spaces in selectors to '%' escapes
			i = 0
			while i < len(selector):
				c = selector[i]
				if c in ' <>&?#%':
					c = '%' + hex(0x100|ord(c))[-2:]
					selector = selector[:i] + c + \
					   selector[i+1:]
				i = i + len(c)
			text = '<LI><A HREF=gopher://' + host + ':' + port + \
				'/' + gtype + selector + '>' + \
				userstring + '</A>\n'
		typestr = gopherlib.type_to_name(gtype)
		text = text + typestr + '\n'
		data = data + text
	data = data + '</UL>\n'
	return data


# Convert a unix directory listing to HTML
def names_to_html(host, path, names, local):
	import string, os
	prefix = '<LI><A HREF=file:'
	if host:
		prefix = prefix + '//' + host
		if path[:1] <> '/': path = '/' + path
	if not path: path = '.'
	if host: header = 'Directory ' + path + ' on ' + host
	else: header = 'Local directory ' + path
	data = '<H1>' + header + '</H1>\n<DIR COMPACT>\n'
	if path[-1:] <> '/': path = path + '/'
	if path not in ('/', './'):
		dirname = os.path.normpath(path + '../')
		text = prefix + dirname + '>../</A>\n'
		data = data + text
	prefix = prefix + path
	names.sort()
	for name in names:
		if local and os.path.isdir(path + name):
			name = name + '/'
		text = prefix + name + '>' + name + '</A>\n'
		data = data + text
	data = data + '</DIR>'
	return data


# Main program for simple testing
def test():
	import sys
	if not sys.argv[1:]:
		sys.argv.append(WWW_HOME)
	for path in sys.argv[1:]:
		print get_document(path)
