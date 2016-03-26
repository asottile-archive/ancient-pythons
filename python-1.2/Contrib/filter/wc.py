#!/usr/local/bin/python

# This is a very complicated example, heck it's bigger than the original
# class, but it was suprisingly easy to write because all I had to worry
# about was what to do at the beginning and end, for each file and each
# line.  Notice the explicit calls to the __init__ and do_file methods
# from the base class.  Also notice how the begin and end functions make
# the class instance rerunable.

from sys import *
from filter import *
from string import *

class file_wc(file_filter) :

	def __init__(self, opts, filenames) :
		self.opts = opts
		self.chars = 0
		self.fchars = 0
		self.words = 0
		self.fwords = 0
		file_filter.__init__(self, filenames)

	def do_file(self) :
		self.fchars = 0
		self.fwords = 0
		file_filter.do_file(self)
		self.chars = self.chars + self.fchars
		self.words = self.words + self.fwords
		for opt in self.opts :
			if opt == "l" :
				print self.fnr,
			elif opt == "w" :
				print self.fwords,
			elif opt == "c" :
				print self.fchars,
		if self.filename != "stdin" :
			print self.filename

	def do_line(self) :
		self.fchars = self.fchars + len(self.line)
		self.fwords = self.fwords + len(split(self.line))

	def begin(self) :
		self.chars = 0
		self.words = 0

	def end(self) :
		if self.filename != "stdin" :
			for opt in self.opts :
				if opt == "l" :
					print self.nr,
				elif opt == "w" :
					print self.words,
				elif opt == "c" :
					print self.chars,
			print "total"

def main() :
	# arg checking could be better...
	if len(argv) > 1 and argv[1][0] == '-' :
		wcer = file_wc(argv[1][1:], argv[2:])
	else :
		wcer = file_wc("lwc", argv[1:])
	wcer.run()

main()
