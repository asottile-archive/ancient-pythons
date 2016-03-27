# Parser for WAIS question files.
# The syntax is (I am really making this up, there is no decent grammar):
# file: node
# node: record | list
# record: '(' keyword (keyword value)* ')'
# list: '(' record* ')'
# value: string | keyword | othertoken | node | '#' bytelist
# bytelist: '(' number* ')'
# Tokens are really almost anything, only strings are treated special;
# keywords are tokens starting with ':'.

import regex
import string


# Class representing a record.
# This is accessed as if it is a dictionary.
# Limited sequential access is also supported: "for k, v in r: ..."
#
class Record:
	#
	def __init__(self, type):
		self.type = type
		self.itemlist = []
	#
	def __repr__(self):
		s = '(:' + self.type + '\n'
		for k, v in self.itemlist:
			v = str(v)
			if '\n' in v:
				lines = string.splitfields(v, '\n')
				v = string.joinfields(lines, '\n  ')
			s = s + '  :' + k + ' ' + v + '\n'
		s = s + ')'
		return s
	#
	def __setitem__(self, keyword, value):
		for i in range(len(self.itemlist)):
			if keyword == self.itemlist[i][0]:
				self.itemlist[i] = (keyword, value)
				return
		self.itemlist.append((keyword, value))
	#
	def __delitem__(self, keyword):
		for i in range(len(self.itemlist)):
			if keyword == self.itemlist[i][0]:
				del self.itemlist[i]
				return
		raise KeyError, 'keyword not in Record: ' + repr(keyword)
	#
	def __getitem__(self, keyword):
		if type(keyword) == type(0):
			# Sequence type access
			return self.itemlist[keyword]
		# Mapping type access
		for k, v in self.itemlist:
			if k == keyword: return v
		raise KeyError, 'keyword not in Record: ' + repr(keyword)
	#
	def __len__(self):
		return len(self.itemlist)
	#
	def keys(self):
		keys = []
		for k, v in self.itemlist:
			keys.append(k)
		return keys
	#
	def has_key(self, keyword):
		for k, v in self.itemlist:
			if k == keyword: return 1
		return 0
	#
	def gettype(self):
		return self.type


# Class representing a list of values.
#
class List:
	#
	def __init__(self, *args):
		self.list = []
		for item in args:
			self.list.append(item)
	#
	def __repr__(self):
		s = '(\n'
		for item in self.list:
			item = str(item)
			if '\n' in item:
				lines = string.splitfields(item, '\n')
				item = string.joinfields(lines, '\n  ')
			s = s + '  ' + item + '\n'
		s = s + ')'
		return s
	#
	def append(self, item):
		self.list.append(item)
	#
	def insert(self, i, item):
		self.list.insert(i, item)
	#
	def remove(self, item):
		self.list.remove(item)
	#
	def __len__(self):
		return len(self.list)
	#
	def __getitem__(self, i):
		return self.list[i]
	#
	def __setitem__(self, i, value):
		self.list[i] = value
	#
	def __delitem__(self, i):
		del self.list[i]
	#
	def __getslice__(self, i, j):
		new = List()
		for item in self.list[i:j]:
			new.append(item)
		return new


# Class representing a list of bytes.
#
class BytesList:
	#
	def __init__(self):
		self.bytes = ''
	#
	def __repr__(self):
		s = '#('
		for byte in self.bytes:
			s = s + ' ' + str(ord(byte))
		s = s + ' )'
		return s
	#
	def append(self, value):
		try:
			i = string.atoi(value)
		except string.atoi_error:
			raise SyntaxError, (value, 'byte')
		try:
			c = chr(i)
		except ValueError:
			raise SyntaxError, (value, 'byte in 0..255')
		self.bytes = self.bytes + c


# Regular expressions used by the tokenizer, and "compiled" versions
#
wspat = '\([ \t\n\r\f]+\|;.*\n\)*'
tokenpat = '[()#"]\|[^()#"; \t\n\r\f]+'
stringpat = '"\(\\\\.\|[^\\"]\)*"'	# "\(\\.\|[^\"]\)*"
wsprog = regex.compile(wspat)
tokenprog = regex.compile(tokenpat)
stringprog = regex.compile(stringpat)


# Parser base class without look-ahead.
# Instantiate each time you want to parse a file.
#
class RealBaseParser:
	#
	def __init__(self, input):
		#
		# 'input' should have a parameterless method readline()
		# which returns the next line, including trailing '\n',
		# or the empty string if there is no more data.
		# An open file will do nicely, as does an instance
		# of StringInput below.
		#
		self.input = input
		self.lineno = 0
		#
		# Reset the scanner interface.
		#
		self.reset()
	#
	def reset(self):
		self.nextline = ''
		self.pos = 0
		self.tokstart = 0
		self.eofseen = 0
	#
	# The real work of getting a token is done here.
	# This is the first place place to look if you think
	# the parser is too slow.
	#
	def getnexttoken(self):
		while 1:
			k = wsprog.match(self.nextline, self.pos)
			if k < 0:
				raise SyntaxError, ('', 'whitespace')
			self.pos = self.pos + k
			k = tokenprog.match(self.nextline, self.pos)
			if k >= 0:
				break
			#
			# End of line hit
			#
			if self.eofseen:
				self.nextline = ''
			else:
				self.nextline = self.input.readline()
			self.pos = self.tokstart = 0
			if not self.nextline:
				if self.eofseen:
					raise EOFError
				self.eofseen = 1
				return ''
			self.lineno = self.lineno + 1
		#
		# Found a token
		#
		self.tokstart, self.pos = self.pos, self.pos + k
		token = self.nextline[self.tokstart:self.pos]
		if token == '"':
			#
			# Get the whole string -- may read more lines
			#
			k = stringprog.match(self.nextline, self.tokstart)
			while k < 0:
				cont = self.input.readline()
				if not cont:
					k = len(self.nextline) - self.tokstart
					break
				self.nextline = self.nextline + cont
				self.lineno = self.lineno + 1
				k = stringprog.match(self.nextline, \
					self.tokstart)
			self.pos = self.tokstart + k
			token = self.nextline[self.tokstart:self.pos]
		return token
	#
	# Default error handlers.
	#
	def reporterror(self, filename, message, fp):
		fp.write(filename)
		fp.write(':' + `self.lineno` + ': ')
		fp.write(message)
		fp.write('\n')
		self.printerrorline(fp)
	#
	def printerrorline(self, fp):
		line = self.nextline
		fp.write(line)
		if line[-1:] <> '\n':
			fp.write('\n')
		for i in range(len(line)):
			if i >= self.tokstart:
				n = max(1, self.pos - i)
				fp.write('^'*n)
				break
			elif line[i] == '\t':
				fp.write('\t')
			elif ' ' <= line[i] < '\177':
				fp.write(' ')
		fp.write('\n')


# Parser base class.  Instantiate each time you want to parse a file.
# This supports a single token look-ahead.
#
class BaseParser(RealBaseParser):
	#
	def reset(self):
		RealBaseParser.reset(self)
		self.pushback = ''
	#
	def peektoken(self):
		if not self.pushback:
			self.pushback = self.getnexttoken()
		return self.pushback
	#
	def gettoken(self):
		if self.pushback:
			token = self.pushback
			self.pushback = ''
		else:
			token = self.getnexttoken()
		if token == '':
			raise EOFError
		return token
	#
	def ungettoken(self, token):
		if self.pushback:
			raise AssertError, 'more than one ungettoken'
		# print 'pushback:', token
		self.pushback = token


# Parser for a node.  Instantiate, and gell getnode() to parse a node.
#
class Parser(BaseParser):
	#
	# Parse a node.  This is highly recursive.
	#
	def getnode(self):
		self.open()
		# This can be either a list or a record
		if self.peektoken() in ('(', ')'): # It's a list
			list = List()
			while self.more():
				list.append(self.getnode())
			self.close()
			return list
		# Not a list, must be a record
		type = self.getkeyword()
		rec = Record(type)
		while self.more():
			keyword = self.getkeyword()
			value = self.getvalue()
			rec[keyword] = value
		self.close()
		return rec
	#
	def getkeyword(self):
		t = self.gettoken()
		if t[0] <> ':' or t == ':':
			raise SyntaxError, (t, ':<keyword>')
		return t[1:]
	#
	def getvalue(self):
		t = self.peektoken()
		if t == '(':
			return self.getnode()
		if t == '#':
			self.expect('#')
			return self.getbyteslist()
		if t == ')':
			raise SyntaxError, (t, '<value>')
		return self.gettoken()
	#
	def getbyteslist(self):
		bytes = BytesList()
		self.open()
		while self.more():
			bytes.append(self.getbyte())
		self.close()
		return bytes
	#
	def getbyte(self):
		return self.gettoken()
	#
	# Shorthands for frequently occurring parsing operations
	#
	def open(self):
		self.expect('(')
	#
	def close(self):
		self.expect(')')
	#
	def expect(self, exp):
		t = self.gettoken()
		if t <> exp:
			raise SyntaxError, (t, exp)
	#
	def more(self):
		if self.peektoken() == ')':
			return 0
		else:
			return 1


# A class to parse from a string
#
class StringInput:
	#
	def __init__(self, string):
		self.string = string
		self.pos = 0
	#
	def __repr__(self):
		return '<StringInput instance, string=' + `self.string` \
			+ ', pos=' + `self.pos` + '>'
	#
	def readline(self):
		string = self.string
		i = self.pos
		n = len(string)
		while i < n:
			if string[i] == '\n':
				i = i+1
				break
			i = i+1
		string = string[self.pos : i]
		self.pos = i
		return string


# Convenience routines to parse a file
#
def parsefile(filename):
	f = open(filename, 'r')
	p = Parser(f)
	result = p.getnode()
	f.close()
	return result
#
def parse(f):
	p = Parser(f)
	return p.getnode()


# Test driver for tokenizer -- reads from stdin
#
def testtokenizer():
	import sys
	p = Parser(sys.stdin)
	try:
		while 1: p.gettoken()
	except EOFError:
		print 'EOF'
	except SyntaxError, msg:
		p.reporterror('<stdin>', 'Syntax error: ' + msg, sys.stderr)


# Test driver for parser -- reads from stdin
#
def testparser():
	import sys
	p = Parser(sys.stdin)
	try:
		x = p.getnode()
	except EOFError:
		print 'unexpected EOF at line', p.lineno
		return
	except SyntaxError, msg:
		if type(msg) == type(()):
			gotten, expected = msg
			msg = 'got ' + `gotten` + ', expected ' + `expected`
		p.reporterror('<stdin>', 'Syntax error: ' + msg, sys.stderr)
		return
	print x
