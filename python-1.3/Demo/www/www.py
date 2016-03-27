#! /usr/local/bin/python

# A simple text-based WWW client.

# This is not intended to compete with WWW's LineMode browser, but to
# have an easily modifiable WWW browser, and also to test various
# components like the formatters and protocol interfaces.


import sys
import os
import string
import getopt
from cmd import Cmd

import fmt
import htmllib
import wwwlib
import wwwutil


PAGE_WIDTH = 80				# Page width (for formatter)


# Default locations of logging files
PLACES = '.wwwplaces'
HISTORY = '.wwwhistory'
BOOKMARKS = '.wwwbookmarks'


# Main program
def main():
	#
	places_file = ''
	history_file = ''
	bookmarks_file = ''
	#
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'b:h:p:')
	except getopt.error, msg:
		sys.stdout = sys.stderr
		print msg
		print 'usage: www [-b file] [-h file] [-p file] [docaddr]'
		print '-b file: bookmarks file, default ~/' + BOOKMARKS
		print '-h file: history file, default ~/' + HISTORY
		print '-p file: places file, default ~/' + PLACES
		print 'docaddr: document address, e.g. scheme://host:port/path'
		print 'system default:', wwwutil.system_home
		if wwwutil.user_home <> wwwutil.system_home:
			print 'user default:', wwwutl.user_home
		print 'user default settable with $WWW_HOME'
		sys.exit(2)
	#
	for o, a in opts:
		if o == '-b': bookmarks_file = a
		if o == '-h': history_file = a
		if o == '-p': places_file = a
	#
	if args:
		if len(args) > 1:
			print 'Too many files -- first one used'
		addr = args[0]
	else:
		addr = ''
	#
	x = WWWCmd()
	#
	places = wwwutil.load_file(places_file, PLACES)
	if places:
		x.places = places
	#
	history = wwwutil.load_file(history_file, HISTORY)
	if history:
		if not addr:
			addr = history[-1]
			history = history[:-1]
		x.history = history
	#
	bookmarks = wwwutil.load_file(bookmarks_file, BOOKMARKS)
	if bookmarks is None: bookmarks = []
	if wwwutil.user_home and wwwutil.user_home not in bookmarks:
		bookmarks.insert(0, wwwutil.user_home)
	if wwwutil.system_home and wwwutil.system_home not in bookmarks:
		bookmarks.insert(0, wwwutil.system_home)
	if bookmarks:
		x.bookmarks = bookmarks
	#
	if not addr:
		addr = wwwutil.user_home
	ok = x.setaddr(addr)
	if not ok and addr <> wwwutil.user_home:
		ok = x.setaddr(wwwutil.user_home)
	if not ok and addr <> wwwutil.system_home:
		ok = x.setaddr(wwwutil.system_home)
	if not ok:
		x.close()
		print '*** Nothing in toplevel menu ***'
		return
	#
	try:
		try:
			x.cmdloop()
		except SystemExit:
			pass
	finally:
		wwwutil.save_file(x.bookmarks, bookmarks_file, BOOKMARKS)
		wwwutil.save_file(x.history + [x.cur_addr], \
			history_file, HISTORY)
		wwwutil.save_file(x.places, places_file, PLACES)


# Class handling the command loop
class WWWCmd(Cmd):
	#
	def __init__(self):
		Cmd.__init__(self)
		self.prompt = 'Which anchor? (h for help) '
		self.cur_addr = ''
		self.cur_data = ''
		self.cur_title = ''
		self.cur_anchors = []
		self.cur_isindex = 0
		self.bookmarks = []
		self.history = []
		self.places = {}
	#
	def close(self):
		pass
	#
	def do_add(self, arg):
		if self.cur_addr in self.bookmarks:
			print '*** Already in list of marks: m',
			print self.bookmarks.index(self.cur_addr)+1
			return
		self.bookmarks.append(self.cur_addr)
		print 'Added as m', len(self.bookmarks)
	do_a = do_add
	#
	def do_back(self, arg):
		if not self.history:
			print '*** No more levels'
			return
		addr = self.history[-1]
		del self.history[-1]
		if not self.setaddr(addr):
			print '*** Lost that link -- try again'
	do_b = do_back
	#
	def do_find(self, arg):
		if not self.cur_isindex:
			print '*** Not an index'
			return
		words = string.split(arg)
		if not words:
			print '*** What do you want to find?'
			return
		scheme, host, port, path, search, anchor = \
			wwwlib.parse_addr(self.cur_addr)
		search = '?' + string.joinfields(words, '+')
		addr = wwwlib.unparse_addr(scheme,host,port,path,search,'')
		self.follow(addr)
	do_f = do_find
	#
	def do_goto(self, arg):
		self.follow(arg)
	do_g = do_goto
	#
	do_h = Cmd.do_help.im_func
	# XXX Very unsatisfactory hack!  It used to read Cmd.do_help but
	# XXX since 0.9.9 that yields an <unbound method> object which
	# XXX can't be passed on transparently to a derived class
	# XXX in this way.  (Maybe Python should be changed?)
	#
	def do_info(self, arg):
		print self.cur_addr
		if self.cur_isindex:
			print '<ISINDEX>'
		if self.cur_title:
			print '<TITLE>' + self.cur_title + '</TITLE>'
	do_i = do_info
	#
	def do_list(self, arg):
		if not self.cur_anchors:
			print '*** No anchors here'
			return
		verbose = (arg == '-v')
		real_stdout = sys.stdout
		pipe = sys.stdout = os.popen('${PAGER-more}', 'w')
		try:
			for i in range(len(self.cur_anchors)):
				label = `[i+1]`
				addr = self.cur_anchors[i]
				if verbose:
					print label, addr
					label = ' '*len(label)
				full = wwwlib.full_addr(self.cur_addr, \
					addr, self.cur_isindex)
				if verbose and full <> addr:
					print label, full
				if self.places.has_key(full):
					t = self.places[full][0]
				else:
					t = None
				if t:
					print label, t
				elif not verbose:
					print label, addr
			sys.stdout = real_stdout
		except IOError, msg:
			sys.stdout = real_stdout
			print '*** IOError:', msg
		except KeyboardInterrupt:
			sys.stdout = real_stdout
			print
		sts = pipe.close()
		if sts:
			print '*** Pager exit status:', sts
	do_l = do_list
	#
	def do_mark(self, arg):
		list = self.bookmarks
		verbose = 0
		if arg == '-v':
			verbose = 1
			words = []
		else:
			words = string.split(arg)
		if words:
			try:
				i = string.atoi(words[0])
			except string.atoi_error:
				print '*** usage: m(ark) [number]'
				return
			if 1 <= i <= len(list):
				self.follow(list[i-1])
			else:
				print '*** recall index out of range',
				print '(' + `1` + '...' + `len(list)` + ')'
			return
		for i in range(len(list)):
			label = 'm ' + `i+1`
			addr = list[i]
			title, exits = self.places[addr]
			if title:
				print label, title
			else:
				print label, addr
			if not verbose:
				continue
			label = ' '*len(label)
			if title:
				print label, addr
			label = label + ' (-->'
			for exit in exits:
				if i+1 >= len(list) or exit != list[i+1]:
					t = self.places[exit][0]
					if t:
						print label, t + ')'
					else:
						print label, exit + ')'
	do_m = do_mark
	#
	def do_places(self, arg):
		real_stdout = sys.stdout
		pipe = sys.stdout = os.popen('${PAGER-more}', 'w')
		try:
			for addr in self.places.keys():
				print addr
				title, exits = self.places[addr]
				if title:
					print '(' + title + ')'
				for exit in exits:
					print '-->', exit
					t = self.places[exit][0]
					if t:
						print '   ', '(' + t + ')'
			sys.stdout = real_stdout
		except IOError, msg:
			sys.stdout = real_stdout
			print '*** IOError:', msg
		except KeyboardInterrupt:
			sys.stdout = real_stdout
			print
		sts = pipe.close()
		if sts:
			print '*** Pager exit status:', sts
	#
	def do_quit(self, arg):
		print '[Goodbye]'
		raise SystemExit
	do_EOF = do_q = do_quit
	#
	def do_recall(self, arg):
		verbose = 0
		hlist = self.history + [self.cur_addr]
		if arg == '-v':
			verbose = 1
			words = []
		else:
			words = string.split(arg)
		if words:
			try:
				i = string.atoi(words[0])
			except string.atoi_error:
				print '*** usage: r(ecall) [number]'
				return
			if 1 <= i <= len(hlist):
				self.follow(hlist[i-1])
			else:
				print '*** recall index out of range',
				print '(' + `1` + '...' + `len(hlist)` + ')'
			return
		for i in range(len(hlist)):
			label = 'r ' + `i+1`
			addr = hlist[i]
			title, exits = self.places[addr]
			if title:
				print label, title
			else:
				print label, addr
			if not verbose:
				continue
			label = ' '*len(label)
			if title:
				print label, addr
			label = label + ' (-->'
			for exit in exits:
				if i+1 >= len(hlist) or exit != hlist[i+1]:
					t = self.places[exit][0]
					if t:
						print label, t + ')'
					else:
						print label, exit + ')'
	do_r = do_recall
	#
	def do_source(self, arg):
		pipe = os.popen('${PAGER-more}', 'w')
		try:
			pipe.write(self.cur_data)
		except IOError, msg:
			print '*** IOError:', msg
		except KeyboardInterrupt:
			print
		sts = pipe.close()
		if sts:
			print '*** Pager exit status:', sts
	do_s = do_source
	#
	def do_top(self, arg):
		self.show()
	do_t = do_top
	#
	def default(self, line):
		try:
			i = string.atoi(string.strip(line))
		except string.atoi_error:
			if self.cur_isindex:
				self.do_find(line)
			else:
				print '*** Unknown command, type h for help'
			return
		if not self.cur_anchors:
			print '*** No anchors here, type u to go up a level'
			return
		if not 1 <= i <= len(self.cur_anchors):
			print '*** Number out of anchor range [1-' + \
				`len(self.cur_anchors)` + '] (l lists anchors)'
			return
		self.follow(self.cur_anchors[i-1])
	#
	def follow(self, addr):
		parent = self.cur_addr
		if self.setaddr(addr):
			self.history.append(parent)
			exits = self.places[parent][1]
			if self.cur_addr in exits:
				exits.remove(self.cur_addr)
			exits.append(self.cur_addr)
			self.prompt = self.baseprompt + '(b=back, h=help) '
	#
	def setaddr(self, addr):
		addr = wwwlib.full_addr(self.cur_addr, addr, \
			self.cur_isindex)
		try:
			data = wwwlib.get_document(addr)
		except (wwwlib.BadAddress, IOError), msg:
			print '***', addr, ':', msg
			return 0
		self.cur_addr = addr
		self.cur_data = data
		self.cur_title = ''
		self.cur_anchors = []
		self.cur_isindex = 0
		self.show()
		#
		if not self.places.has_key(self.cur_addr):
			exits = []
		else:
			exits = self.places[self.cur_addr][1]
		self.places[self.cur_addr] = (self.cur_title, exits)
		#
		if self.cur_isindex and self.cur_anchors:
			prompt = 'Keyword or anchor? '
		elif self.cur_isindex:
			prompt = 'Find keyword? '
		elif self.cur_anchors:
			prompt = 'Which anchor? '
		else:
			prompt = 'What now? '
		self.baseprompt = prompt
		self.prompt = prompt + '(q == quit, h == help) '
		return 1
	#
	def show(self):
		pipe = os.popen('${PAGER-more}', 'w')
		fmtr = fmt.WritingFormatter(pipe, PAGE_WIDTH)
		parser = htmllib.FormattingParser(fmtr, \
						      htmllib.NullStylesheet)
		try:
			parser.feed(self.cur_data)
			parser.close()
			pipe.write('\n\n')
		except IOError, msg:
			print '*** IOError:', msg
		except KeyboardInterrupt:
			print
		sts = pipe.close()
		if sts:
			print '*** Pager exit status:', sts
		self.cur_anchors = parser.anchors
		self.cur_title = parser.title
		self.cur_isindex = parser.isindex


try:
	main()
except KeyboardInterrupt:
	print
	print '[Intr]'
