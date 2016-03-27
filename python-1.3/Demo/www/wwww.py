#! /usr/local/bin/python

# A stdwin-based Windowing WWW client (hence 4 W's!)


import sys
sys.path.append('/ufs/guido/src/www')
import os
import string
import marshal
import getopt
import stdwin
import mainloop
from stdwinevents import *
import fmt
import htmllib
import wwwlib
import wwwutil


# Parametrizations
MAXHIST = 40				# Max number of history entries shown
MAXANCH = 40				# Max number of anchors shown
WAITCURSOR = 'watch'
READYCURSOR = 'arrow'


# Default locations of logging files
PLACES = '.wwwplaces'
HISTORY = '.wwwhistory'
BOOKMARKS = '.wwwbookmarks'


# Globals managed by main
places = {}
bookmarks = []
history_file = ''
bookmarks_menu = None


# Enums indicating what to do with history when following a link
H_POP = -1
H_NOP = 0
H_PUSH = 1


def main():
	global places, bookmarks
	global history_file, places_file, bookmarks_file
	#
	help = 0
	raw_mode = 0
	server_mode = 0
	#
	places_file = ''
	bookmarks_file = ''
	#
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'b:h:p:rsH')
	except getopt.error, msg:
		sys.stdout = sys.stderr
		print msg
		print \
 'usage: wwww [-b file] [-h file] [-p file] [-r] [-H] [docaddr ...]'
		print '-b file: bookmarks file, default ~/' + BOOKMARKS
		print '-h file: history file, default ~/' + HISTORY
		print '-p file: history file, default ~/' + PLACES
		print '-r     : start windows in raw mode'
		print '-s     : start in server mode'
		print '-H     : start up with help window'
		print 'docaddr: document address, e.g. scheme://host:port/path'
		print 'system default:', wwwutil.system_home
		if os.environ.has_key('WWW_HOME'):
			print 'user default:', wwwutil.user_home
		print 'user default settable with $WWW_HOME'
		sys.exit(2)
	#
	for o, a in opts:
		if o == '-b': bookmarks_file = a
		if o == '-h': history_file = a
		if o == '-p': places_file = a
		if o == '-r': raw_mode = 1
		if o == '-s': server_mode = 1
		if o == '-H': help = 1
	#
	places = wwwutil.load_file(places_file, PLACES)
	if places is None: places = {}
	#
	bookmarks = wwwutil.load_file(bookmarks_file, BOOKMARKS)
	if bookmarks is None: bookmarks = []
	if wwwutil.user_home and wwwutil.user_home not in bookmarks:
		bookmarks.insert(0, wwwutil.user_home)
	if wwwutil.system_home and wwwutil.system_home not in bookmarks:
		bookmarks.insert(0, wwwutil.system_home)
	#
	history = wwwutil.load_file(history_file, HISTORY)
	if history is None: history = []
	if not server_mode and not args and history:
		args.append(history[-1])
		del history[-1]
	#
	if server_mode:
		start_server()
	#
	stdwin.setdefwinsize(0, 0)
	for addr in args:
		w = WWWWindow()
		w.set_raw_mode(raw_mode)
		if not w.setaddr(addr):
			w.close()
		else:
			w.set_history(history)
	#
	if not server_mode and mainloop.countwindows() == 0:
		# Fallback -- try default pages
		for addr in wwwutil.user_home, wwwutil.system_home:
			if addr not in args:
				w = WWWWindow()
				w.set_raw_mode(raw_mode)
				if not w.setaddr(addr):
					w.close()
				else:
					w.set_history(history)
					break
	#
	if help or not server_mode and mainloop.countwindows() == 0:
		make_help_window()
	#
	mainloop.mainloop()


# Start the help server (for -s option: server_mode)
server_socket = None
def start_server():
	global server_socket
	import socket
	server_socket = s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.bind('', 4000)
	except socket.error, msg:
		if type(msg) == type(()) and len(msg) == 2 and msg[0] == 114:
			print 'A help server is already running -- exit.'
			sys.exit(0)
		else:
			raise socket.error, msg
	print 'Starting server mode'
	mainloop.registerfd(s, 'r', handle_server_message)


# Handle a server message.
# Format is '<wname> <function> <argument> ...'
# This first looks for a window named <wname>, and opens one if necessary.
# Then it calls the window's method msg_<function> with the argument
# list as argument, as a list of strings.
def handle_server_message(*args):
	data, clientaddr = server_socket.recvfrom(1024)
	words = string.split(data)
	if len(words) < 2:
		print 'Bad message from', clientaddr[0], ':', `data`
		return
	wname = words[0]
	function = words[1]
	try:
		meth = getattr(WWWWindow, 'msg_' + function)
	except AttributeError:
		print 'Bad function', `function`, 'in message from', \
			clientaddr[0], ':', `data`
		return
	##print 'Message from', clientaddr[0], ':', `data`
	new = 0
	for w in allwindows:
		if w.server_name == wname:
			break
	else:
		print 'Creating new window named', `wname`
		stdwin.setdefwinsize(0, 0)
		w = WWWWindow()
		w.server_name = wname
		new = 1
	try:
		getattr(w, 'msg_' + function)(words[2:], clientaddr)
	except:
		print '***', sys.exc_type, ':', `sys.exc_value`


# Make the menu of bookmarks
def make_bookmarks_menu(raw_mode):
	global bookmarks_menu
	if bookmarks_menu is not None:
		bookmarks_menu.close()
		bookmarks_menu = None
	bookmarks_menu = menu = stdwin.menucreate('Bookmarks')
	for addr in bookmarks:
		if not raw_mode and places.has_key(addr):
			t = places[addr][0]
			if string.strip(t): addr = t
		menu.additem(addr)


# Misc. globals
charnames = {'?': 'question', ' ': 'space'}
allwindows = []
last_regex = None


class WWWWindow:
	#
	def __init__(self):
		# For server
		self.server_name = None
		# Windowing state
		self.window = stdwin.open('WWWW - by Guido van Rossum')
		self.window.setwincursor(WAITCURSOR)
		self.last_mouse_down = None
		self.last_msg = ''
		# Current document state
		self.cur_addr = ''
		self.cur_data = ''
		self.cur_anchors = []
		self.cur_anchornames = []
		self.cur_anchortypes = []
		self.cur_isindex = 0
		self.cur_backend = None
		# User state
		self.raw_mode = 0
		# Logging state
		self.history = []
		# Menus
		self.history_menu = None
		self.anchors_menu = None
		self.make_command_menu()
		self.make_bookmarks_menu()
		# Register us for events
		self.window.dispatch = self.dispatch
		mainloop.register(self.window)
		allwindows.append(self)
		# Initialize cur_backend
		self.setrawdata('', '')
	#
	def make_command_menu(self):
		self.command_menu = menu = self.window.menucreate('Commands')
		self.command_call = []
		#
		self.add_cmd('Help', '?', self.key_question)
		#
		self.add_cmd('', '', None) # ----------------------------------
		#
		self.find_index = len(self.command_call)
		self.add_cmd('Find keyword(s) in index...', 'i', self.key_i)
		menu.enable(self.find_index, self.cur_isindex)
		#
		self.add_cmd('Find regexp...', 'f', self.key_f)
		#
		self.add_cmd('Find aGain', 'g', self.key_g)
		#
		self.add_cmd('', '', None) # ----------------------------------
		#
		self.back_index = len(self.command_call)
		self.add_cmd('Back up', 'b', self.key_b)
		menu.enable(self.back_index, len(self.history) > 0)
		#
		self.add_cmd('User home', 'H', self.key_H)
		#
		self.add_cmd('System home', 'S', self.key_S)
		#
		self.add_cmd('Go to ...', 'G', self.key_G)
		#
		self.add_cmd('', '', None) # ----------------------------------
		#
		self.add_cmd('Up', 'u', self.key_u)
		#
		self.add_cmd('Down', 'd', self.key_d)
		#
		self.add_cmd('Next', 'n', self.key_n)
		#
		self.add_cmd('Prev', 'p', self.key_p)
		#
		self.add_cmd('Traverse (space)', ' ', self.key_space)
		#
		self.add_cmd('', '', None) # ----------------------------------
		#
		self.raw_index = len(self.command_call)
		self.add_cmd('Show raw addresses', 'r', self.key_r)
		menu.check(self.raw_index, self.raw_mode)
		#
		self.add_cmd('Add to Bookmarks menu', 'a', self.key_a)
		#
		self.add_cmd('', '', None) # ----------------------------------
		#
		self.add_cmd('Clone window', 'k', self.key_k)
		#
		self.add_cmd('Show source window', 's', self.key_s)
		#
		self.add_cmd('', '', None) # ----------------------------------
		#
		self.add_cmd('Save...', '', self.save)
		#
		self.add_cmd('Save source...', '', self.save_source)
		#
		self.add_cmd('', '', None) # ----------------------------------
		#
		self.add_cmd('Quit (close window)', 'q', self.key_q)
	#
	def add_cmd(self, label, key, func):
		self.command_call.append(func)
		if key:
			self.command_menu.additem(label, key)
		else:
			self.command_menu.additem(label)
	#
	def set_raw_mode(self, raw_mode):
		self.raw_mode = raw_mode
		self.make_title()
		self.command_menu.check(self.raw_index, self.raw_mode)
		self.make_anchors_menu()
		self.make_history_menu() # Implies make_bookmarks_menu
	#
	def set_history(self, history):
		self.history = history[:]
		self.make_history_menu()
	#
	def new(self):
		stdwin.setdefwinsize(self.window.getwinsize())
		w = WWWWindow()
		w.set_raw_mode(self.raw_mode)
		return w
	#
	def close(self):
		if self in allwindows:
			allwindows.remove(self)
		mainloop.unregister(self.window)
		self.window.dispatch = None
		self.window.close()
		if self.history:
			wwwutil.save_file(self.history + [self.cur_addr], \
					  history_file, HISTORY)
		wwwutil.save_file(bookmarks, bookmarks_file, BOOKMARKS)
		wwwutil.save_file(places, places_file, PLACES)
	#
	def dispatch(self, event):
		type, win, detail = event
		if type == WE_CLOSE:
			self.close()
		if type == WE_SIZE:
			self.resize()
		if type == WE_DRAW:
			self.redraw(detail)
		if type == WE_CHAR:
			self.character(detail)
		if type == WE_COMMAND:
			if detail == WC_CANCEL:
				self.close()
		if type == WE_MOUSE_DOWN:
			self.mouse_down(detail)
		if type == WE_MOUSE_MOVE:
			self.mouse_move(detail)
		if type == WE_MOUSE_UP:
			self.mouse_up(detail)
		if type == WE_MENU:
			self.menu(detail)
	#
	def menu(self, (menu, item)):
		if menu is self.command_menu:
			self.command_call[item]()
		if menu is self.anchors_menu:
			self.follow(self.cur_anchors[item])
		if menu is self.history_menu:
			offset = max(0, len(self.history) - MAXHIST)
			if 0 <= offset + item < len(self.history):
				self.follow(self.history[offset + item], H_POP)
		if menu is bookmarks_menu:
			self.follow(bookmarks[item])
	#
	def mouse_down(self, detail):
		h, v = detail[0]
		button = detail[2]
		mask = detail[3]
		if not mask&(WM_SHIFT|WM_CONTROL):
			hits = self.cur_backend.hitcheck(h, v)
			if hits:
				# Anchor hit -- triggered on mouse up
				self.last_mouse_down = None
				return
		long1 = long2 = self.cur_backend.whereis(stdwin, h, v)
		if not long1:
			self.last_mouse_down = None
			self.cur_backend.setselection(None)
			return
		if (button == 3 or mask&WM_SHIFT) and self.last_mouse_down:
			pass # Remember the old last_mouse_down
		else:
			self.last_mouse_down = detail
		long1, long2 = self.roundpositions(long1, long2)
		self.cur_backend.setselection((long1, long2))
	#
	def roundpositions(self, long1, long2):
		if long1 > long2:
			long1, long2 = long2, long1
		clicks = self.last_mouse_down[1]
		if clicks > 2:
			long1, long2 = \
			    self.cur_backend.roundtoparagraphs(long1, long2)
		elif clicks > 1:
			long1, long2 = \
			    self.cur_backend.roundtowords(long1, long2)
		return long1, long2
	#
	def mouse_move(self, detail):
		if not self.last_mouse_down:
			return
		h1, v1 = self.last_mouse_down[0]
		h2, v2 = detail[0]
		long1 = self.cur_backend.whereis(stdwin, h1, v1)
		long2 = self.cur_backend.whereis(stdwin, h2, v2)
		if long1 and long2:
			long1, long2 = self.roundpositions(long1, long2)
			self.cur_backend.setselection((long1, long2))
	#
	def mouse_up(self, detail):
		if self.last_mouse_down:
			h1, v1 = self.last_mouse_down[0]
			h2, v2 = detail[0]
			long1 = self.cur_backend.whereis(stdwin, h1, v1)
			long2 = self.cur_backend.whereis(stdwin, h2, v2)
			if not long1 or not long2:
				return
			long1, long2 = self.roundpositions(long1, long2)
			self.cur_backend.setselection((long1, long2))
			#
			selection = self.cur_backend.extractpart(long1, long2)
			if not selection:
				return
			if not self.window.setselection(WS_PRIMARY, selection):
				# Meaning some other application got it now
				stdwin.fleep()
				return
			stdwin.rotatecutbuffers(1)
			stdwin.setcutbuffer(0, selection)
			return
		h, v = detail[0]
		hits = self.cur_backend.hitcheck(h, v)
		if not hits:
			return
		if len(hits) > 1:
			stdwin.message('Please click in exactly one anchor')
			return
		id = hits[0]
		if 1 <= id <= len(self.cur_anchors):
			addr = self.cur_anchors[id-1]
			name = self.cur_anchornames[id-1]
			type = self.cur_anchortypes[id-1]
			button = detail[2]
			if button == 2:
				if name:
					msg = 'NAME="' + name + '" '
				else:
					msg = ''
				if addr:
					msg = msg + 'HREF="' + addr + '"'
				stdwin.message(msg)
			elif addr[:7] == 'telnet:':
				self.telnet(addr)
			elif button == 3 and addr and addr[0] <> '#':
				addr = self.full_addr(addr)
				w = self.new()
				history = self.history + [self.cur_addr]
				if not w.setaddr(addr):
					w.close()
					stdwin.message(addr + ': ' + \
						self.last_msg)
				else:
					w.set_history(history)
			else:
				self.follow(addr)
		else:
			stdwin.message('Strange - bad anchor id???')
	#
	def character(self, c):
		if charnames.has_key(c):
			c = charnames[c]
		try:
			method = getattr(self, 'key_' + c)
		except AttributeError:
			stdwin.fleep()
			return
		method()
	#
	# Message handlers for server mode
	#
	def msg_null(self, args, clientaddr):
		pass
	#
	def msg_close(self, args, clientaddr):
		self.close()
	#
	def msg_echo(self, args, clientaddr):
		reply = self.server_name + ' echo ' + string.join(args)
		server_socket.sendto(reply, clientaddr)
	#
	def msg_goto(self, args, clientaddr):
		if len(args) < 1:
			print 'msg_goto: No address given'
			return
		addr = self.full_addr(args[0])
		if addr <> self.cur_addr and \
				not self.followok(addr, H_PUSH, 1):
			print 'msg_goto: Follow of', addr, 'failed'
			return
		if args[1:]:
			self.find(args[1])
	#
	def msg_find(self, args, clientaddr):
		if not args: pat = ''
		else: pat = args[0]
		self.find(pat)
	#
	# Special functions for Emacs INFO style navigation in documents
	# generated by texi2html.py
	#
	def gotype(self, type, hist):
		if type in self.cur_anchortypes:
			i = self.cur_anchortypes.index(type)
			addr = self.cur_anchors[i]
			if addr:
				return self.followok(addr, hist, 1)
		return 0
	#
	def gobytype(self, type, hist):
		if not self.gotype(type, hist):
			stdwin.fleep()
	#
	def key_space(self): # traverse
		if self.gotype('menu', H_PUSH) or self.gotype('next', H_NOP):
			return
		while 1:
			if not self.gotype('up', H_POP):
				stdwin.fleep()
				return
			if self.gotype('next', H_NOP):
				return
	#
	def key_u(self): # up
		self.gobytype('up', H_POP)
	#
	def key_d(self): # down
		self.gobytype('menu', H_PUSH)
	#
	def key_n(self): # next
		self.gobytype('next', H_NOP)
	#
	def key_p(self): # prev
		self.gobytype('prev', H_NOP)
	#
	def key_t(self): # top
		self.gobytype('top', H_POP)
	#
	# Other keyboard shortcut handlers
	#
	def key_a(self): # add to global list of bookmarks
		if self.cur_addr in bookmarks:
			bookmarks.remove(self.cur_addr)
		bookmarks.append(self.cur_addr)
		self.make_bookmarks_menu()
	#
	def key_f(self): # Find string
		if last_regex:
			prog, pat = last_regex
		else:
			prog, pat = None, ''
		try:
			pat = stdwin.askstr('Enter regular expression:', pat)
		except KeyboardInterrupt:
			return
		self.find(pat)
	#
	def key_g(self): # find aGain
		self.find('')
	#
	def find(self, pat):
		import regex
		global last_regex
		if not pat:
			if last_regex:
				prog, pat = last_regex
			else:
				prog, pat = None, ''
			if not prog:
				stdwin.message('No previous regexp')
				return
		else:
			try:
				prog = regex.compile(string.lower(pat))
			except regex.error, msg:
				if type(msg) <> type(''): msg = `msg`
				stdwin.message(msg)
				return
			last_regex = prog, pat
		if not self.cur_backend.search(prog):
			stdwin.fleep()
	#
	def key_H(self): # User home
		self.follow(wwwutil.user_home)
	#
	def key_S(self): # System home
		self.follow(wwwutil.system_home)
	#
	def key_b(self): # back
		self.back()
	#
	def key_i(self): # find keyword in index
		try:
			reply = stdwin.askstr('Find keyword(s) in index:', '')
		except KeyboardInterrupt:
			return
		words = string.split(reply)
		if not words:
			return
		scheme, host, port, path, search, anchor = \
			wwwlib.parse_addr(self.cur_addr)
		if len(search) > 1: hist = H_NOP
		else: hist = H_PUSH
		search = '?' + string.joinfields(words, '+')
		addr = wwwlib.unparse_addr(scheme,host,port,path,search,'')
		self.follow(addr, hist)
	#
	def key_G(self): # goto
		try:
			reply = stdwin.askstr('Go to document:', self.cur_addr)
		except KeyboardInterrupt:
			return
		addr = string.strip(reply)
		if not addr:
			return
		self.follow(addr)
	#
	def key_h(self): # help
		make_help_window()
	key_question = key_h
	#
	def key_k(self): # clone
		w = self.new()
		w.setrawdata(self.cur_addr, self.cur_data)
		w.set_history(self.history)
	#
	def key_q(self): # quit (closes current window only)
		self.close()
	#
	def key_r(self): # raw (toggle)
		self.set_raw_mode(not self.raw_mode)
	#
	def key_s(self): # source
		w = self.new()
		w.setrawdata(self.cur_addr, '<PLAINTEXT>' + self.cur_data)
		w.set_raw_mode(1)
	#
	def telnet(self, addr):
		scheme, host, port, path, search, anchor = \
			wwwlib.parse_addr(addr)
		if scheme <> 'telnet':
			print 'Not a telnet address'
			return
		cmd = 'telnet ' + host
		cmd = 'xterm -e ' + cmd + ' &'
		sts = os.system(cmd)
		if sts:
			print `cmd`
			print 'Exit status:', sts
	#
	def follow(self, addr, *args):
		# Process optional arguments [hist, [warn]]
		if args: hist = args[0]
		else: hist = H_PUSH
		if args[1:]: warn = args[1]
		else: warn = 1
		dummy = self.followok(addr, hist, warn)
	#
	def followok(self, addr, hist, warn):
		# Check for empty address
		if not addr: return 1 # We're already here
		# Check if there's just an anchor
		if addr[0] == '#':
			anchor = addr[1:]
			if anchor not in self.cur_anchornames:
				if warn:
					stdwin.fleep() # Anchor not found
				return 0
			id = 1 + self.cur_anchornames.index(anchor)
			self.cur_backend.showanchor(id)
			return 1
		# Set the address, bail out if we can't
		parent = self.cur_addr
		if not self.setaddr(addr):
			if warn:
				stdwin.message(addr + ' :' + self.last_msg)
			return 0
		# Fix the exits in the places directory
		exits = places[parent][1]
		if self.cur_addr in exits:
			exits.remove(self.cur_addr)
		exits.append(self.cur_addr)
		# Fix the history
		if hist == H_NOP:
			pass
		elif hist == H_POP:
			if self.history and self.history[-1] == self.cur_addr:
				del self.history[-1]
		elif hist == H_PUSH:
			if parent:
				self.history.append(parent)
		else:
			print 'Strange hist:', hist
		self.make_history_menu()
		return 1
	#
	def back(self):
		if not self.history:
			stdwin.fleep()
			return
		self.follow(self.history[-1], H_POP)
	#
	def save(self):
		try:
			file = stdwin.askfile('Save to file:', '', 1)
		except KeyboardInterrupt:
			return
		file = string.strip(file)
		if not file:
			return
		try:
			f = open(file, 'w')
		except IOError, msg:
			stdwin.message(file + ': ' + msg)
			return
		self.window.setwincursor(WAITCURSOR)
		fmtr = fmt.WritingFormatter(f, 72)
		parser = htmllib.FormattingParser(fmtr, \
						      htmllib.NullStylesheet)
		try:
			parser.feed(self.cur_data)
			parser.close()
			f.write('\n')
			f.close()
		except IOError, msg:
			stdwin.message(file + ': ' + msg)
		self.window.setwincursor(READYCURSOR)
	#
	def save_source(self):
		try:
			file = stdwin.askfile('Save source to file:', '', 1)
		except KeyboardInterrupt:
			return
		file = string.strip(file)
		if not file:
			return
		try:
			f = open(file, 'w')
			f.write(self.cur_data)
			f.close()
		except IOError, msg:
			stdwin.message(file + ': ' + msg)
	#
	def setaddr(self, addr):
		self.window.setwincursor(WAITCURSOR)
		savetitle = self.window.gettitle()
		full = self.full_addr(addr)
		self.window.settitle('Retrieving ' + full + ' ...')
		try:
			data = wwwlib.get_document(full)
		except:
			msg = sys.exc_value
			if type(msg) <> type(''):
				msg = `msg`
			self.last_msg = msg
			self.window.settitle(savetitle)
			self.window.setwincursor(READYCURSOR)
			return 0
		self.setrawdata(full, data)
		return 1
	#
	def setrawdata(self, addr, data):
		if '#' in addr:
			i = string.index(addr, '#')
			addr, anchor = addr[:i], addr[i+1:]
		else:
			anchor = ''
		self.cur_addr = addr
		self.cur_data = data
		#
		self.window.settitle('Formatting ' + addr + ' ...')
		self.window.setorigin(0, 0)
		self.window.setdocsize(0, 0)
		self.window.change((0, 0), (10000, 30000)) # XXX
		#
		# XXX The X11 version here assumes that setdocsize()
		# generates a WE_DRAW event
		b = fmt.StdwinBackEnd(self.window, 0)
		b.d.setfont(htmllib.StdwinStylesheet.stdfontset[0])
		##b = fmt.StdwinBackEnd(self.window, 1) # Mac version
		f = fmt.BaseFormatter(b.d, b)
		p = htmllib.AnchoringParser(f, htmllib.StdwinStylesheet)
		p.feed(self.cur_data)
		p.close()
		b.finish()
		#
		self.cur_backend = b
		self.cur_anchors = p.anchors
		self.cur_anchornames = p.anchornames
		self.cur_anchortypes = p.anchortypes
		self.cur_isindex = p.isindex
		#
		if not places.has_key(self.cur_addr):
			exits = []
		else:
			exits = places[self.cur_addr][1]
		places[self.cur_addr] = (p.title, exits)
		#
		self.command_menu.enable(self.find_index, self.cur_isindex)
		self.make_title()
		self.make_anchors_menu()
		self.window.setwincursor(READYCURSOR)
		#
		if anchor:
			if anchor not in self.cur_anchornames:
				stdwin.fleep() # Anchor not found
				return
			id = 1 + self.cur_anchornames.index(anchor)
			self.cur_backend.showanchor(id)
			return
	#
	def make_title(self):
		title = self.nice_addr(self.cur_addr)
		if self.cur_isindex:
			title = title + ' (INDEX)'
		self.window.settitle(title)
	#
	def make_anchors_menu(self):
		if self.anchors_menu:
			self.anchors_menu.close()
			self.anchors_menu = None
		if not self.cur_anchors:
			return
		self.anchors_menu = menu = self.window.menucreate('Links')
		for addr in self.cur_anchors[:MAXANCH]:
			menu.additem(self.nice_addr(addr))
	#
	def make_history_menu(self):
		if self.history_menu:
			self.history_menu.close()
			self.history_menu = None
		self.command_menu.enable(self.back_index, (self.history <> []))
		self.history_menu = menu = self.window.menucreate('History')
		i = 0
		for addr in self.history[-MAXHIST:]:
			menu.additem(self.nice_addr(addr))
			i = i+1
		menu.additem(self.nice_addr(self.cur_addr))
		menu.check(i, 1)
		self.make_bookmarks_menu()
	#
	def make_bookmarks_menu(self):
		make_bookmarks_menu(self.raw_mode)
	#
	def resize(self):
		self.cur_backend.resize()
	#
	def redraw(self, area):
		if self.cur_backend:
			self.window.setwincursor(WAITCURSOR)
			self.cur_backend.redraw(area)
			self.window.setwincursor(READYCURSOR)
	#
	def full_addr(self, addr):
		return wwwlib.full_addr(self.cur_addr, addr)
	#
	def nice_addr(self, addr):
		if self.raw_mode:
			return addr
		else:
			full = self.full_addr(addr)
			if places.has_key(full):
				t = places[full][0]
				if string.strip(t): return t
			return addr


def make_help_window():
	stdwin.setdefwinsize(500, 350)
	w = WWWWindow()
	d = '<TITLE>WWWW Help</TITLE>\n'
	d = d + '<H1>WWWW User Interface Help</H1>\n'
	d = d + 'Underlined text is linked to other documents.<P>\n'
	d = d + 'Click left to follow a link.<P>\n'
	d = d + 'Click middle to show where a link leads.<P>\n'
	d = d + 'Click right to follow a link in a new window.<P>\n'
	w.setrawdata('builtin:help', d)


try:
	main()
except KeyboardInterrupt:
	print
	print '[Intr]'
