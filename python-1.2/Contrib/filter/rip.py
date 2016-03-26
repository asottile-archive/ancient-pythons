#!/usr/local/bin/python

# Finally a real example, I use this filter to rip noise headers out of
# mail archives.  It's rude and crude and but it took longer to decide
# what headers to rip out than to write the code.  Typically this will
# trim 10 to 40% out of sendmail or mmdf mailbox.

from sys import *
from string import *
from regex import *
from regex_syntax import *
from filter import *

pat = "^" + "Received:"
pat = pat + "|^" + "MMDF-Warning:"
pat = pat + "|^" + "X-Mts:"
pat = pat + "|^" + "X-Mailer:"
pat = pat + "|^" + "X-Sun-Charset:"
pat = pat + "|^" + "X-Filter:"
pat = pat + "|^" + "X-Face:"
pat = pat + "|^" + "X-Zippy:"
pat = pat + "|^" + "Source-Info:"
pat = pat + "|^" + "Precedence:"
pat = pat + "|^" + "Encoding:"
pat = pat + "|^" + "Planet-Of-Origin:"
pat = pat + "|^" + "MIME-Version:"
pat = pat + "|^" + "Mime-Version:"
pat = pat + "|^" + "Content-ID:"
pat = pat + "|^" + "Content-Id:"
pat = pat + "|^" + "Content-Length:"
pat = pat + "|^" + "Content-length:"
pat = pat + "|^" + "Content-Transfer-Encoding:"
pat = pat + "|^" + "Content-transfer-encoding:"
pat = pat + "|^" + "Content-Type:"
pat = pat + "|^" + "Content-type:"

set_syntax(RE_SYNTAX_EGREP)

class file_rip(file_filter) :

	def __init__(self, filenames) :
		self.ripping = 0
		file_filter.__init__(self, filenames)

	def do_line(self) :
		if search(pat, self.line) != -1 :
			self.ripping = 1
		elif self.ripping == 1 and find(" \t", self.line[0]) >= 0 :
			pass
		else :
			self.ripping = 0
			print self.line,

def main() :
	ripper = file_rip(argv[1:])
	ripper.run()

main()
