#!/usr/local/bin/python

# This slightly more complicated example emulates the basic form of
# grep.  It derives a new class from file_filter and overloads the
# __init__ and do_line methods.  Notice how it explicitly calls the base
# classes __init__ method.  The main function also does a bit more work
# to process the command line arguments.

from sys import *
from regex import *
from filter import *

class file_grep(file_filter) :

	def __init__(self, pat, filenames) :
		self.pat = pat
		file_filter.__init__(self, filenames)

	def do_line(self) :
		if search(self.pat, self.line) != -1 :
			print self.filename + ":" + self.line,

def main() :
	if len(argv) < 2 :
		perror("You must specify a pattern")
		exit(1)
	grepper = file_grep(argv[1], argv[2:])
	grepper.run()

main()
