from sys import *
from regex import *

def perror(*elist) :
	for e in elist :
		stderr.write(str(e) + " ")
	stderr.write("\n")
	
class file_filter :

	def __init__(self, filenames) :
		self.filenames = filenames
		self.filename = "stdin"
		self.file = stdin
		self.line = ""
		self.nr = 0
		self.fnr = 0

	def run(self) :
		self.nr = 0
		self.fnr = 0		
		self.begin()
		if not self.filenames :
			self.filename = "stdin"
			self.file = stdin
			self.do_file()
		else :
		    for self.filename in self.filenames :
			self.fnr = 0
			try :
				self.file = open(self.filename)
			except IOError, msg :
				perror("Cannot open:", self.filename, msg)
				continue
			self.do_file()
			self.file.close()
		self.end()

	def do_file(self) :
		while 1 :
			self.line = self.file.readline()
			if self.line == "" : break
			self.nr = self.nr + 1
			self.fnr = self.fnr + 1
			self.do_line()

	def do_line(self) :
		print self.line,

	def begin(self) :
		pass

	def end(self) :
		pass
