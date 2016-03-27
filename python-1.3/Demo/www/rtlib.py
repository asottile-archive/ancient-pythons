# Parser for MIME Richtext.

# The official definition of Richtext prescribes a different handling
# of invalid input than is done by our SGML parser base class.
# However, for valid richtext the interpretation will be correct.
# (Possibly we could make the behaviour of the SGML parser more
# flexible, e.g. define a regular expression that recognizes tags?)


import regex
import string
import sgmllib


wordprog = regex.compile('[^ \t\n]*')
spaceprog = regex.compile('[ \t\n]*')


class FormattingParser(sgmllib.SGMLParser):

	entitydefs = {}			# Richtext doesn't use entities

	def __init__(self, formatter, stylesheet):
		sgmllib.SGMLParser.__init__(self)
		self.fmt = formatter
		self.stl = stylesheet
		self.savetext = None
		self.skip = 0
		self.comment = 0
		self.font = 'roman'
		self.size = 0
		self.just = 'l'
		self.leftindent = 0
		self.rightindent = 0
		self.fontstack = []
		self.sizestack = []
		self.juststack = []
		self.leftstack = []
		self.rightstack = []

	def handle_text(self, text):
		if self.skip > 0: return
		if self.savetext is not None:
			self.savetext = self.savetext + text
			return
		i = 0
		n = len(text)
		while i < n:
			j = i + wordprog.match(text, i)
			word = text[i:j]
			i = j + spaceprog.match(text, j)
			self.fmt.addword(word, i-j)

	handle_literal = handle_text	# XXX not used anyway???

	def passfont(self):
		self.fmt.setfont(self.stl.makefont(self.font, self.size))

	def pushfont(self, font):
		self.fontstack.append(self.font)
		self.font = font
		self.passfont()

	def popfont(self):
		self.font = self.fontstack[-1]
		del self.fontstack[-1]
		self.passfont()

	def pushsize(self, size):
		self.sizestack.append(self.size)
		self.size = size
		self.passfont()

	def popsize(self):
		self.size = self.sizestack[-1]
		del self.sizestack[-1]
		self.passfont()

	def pushjust(self, just):
		self.juststack.append(self.just)
		self.just = just
		self.fmt.setjust(self.just)

	def popjust(self):
		self.just = self.juststack[-1]
		del self.juststack[-1]
		self.fmt.setjust(self.just)

	def pushleft(self, leftindent):
		self.leftstack.append(self.leftindent)
		self.leftindent = leftindent
		self.fmt.setleftindent(self.leftindent)

	def popleft(self):
		self.leftindent = self.leftstack[-1]
		del self.leftstack[-1]
		self.fmt.setleftindent(self.leftindent)

	def pushright(self, rightindent):
		self.rightstack.append(self.rightindent)
		self.rightindent = rightindent
		self.fmt.setrightindent(self.rightindent)

	def popright(self):
		self.rightindent = self.rightstack[-1]
		del self.rightstack[-1]
		self.fmt.setrightindent(self.rightindent)

	# Set nesting literal end pattern
	def setnestingliteral(self, tag):
		re = '</?'
		for c in tag:
			c, C = string.lower(c), string.upper(c)
			if c == C:
				if c in '\\.*+?[^$':
					c = '\\' + c
				re = re + c
			else:
				re = re + '[' + c + C + ']'
		re = re + '>'
		self.litprog = regex.compile(re)

	def do_lt(self, attrs): self.handle_text('<')
	def do_nl(self, attrs): self.fmt.flush()
	def do_np(self, attrs): self.fmt.flush() ### What else?

	def bgn_comment(self, attrs):
		self.comment = self.comment + 1
		self.skip = self.skip + 1
		self.setnestingliteral('comment')
	def end_comment(self, attrs):
		self.skip = self.skip - 1
		self.comment = self.comment - 1
		if self.comment > 0:
			self.setnestingliteral('comment')

	def ignore_bgn(self, attrs): self.skip = self.skip + 1
	def ignore_end(self, attrs): self.skip = self.skip - 1

	def bgn_bold(self, attrs): self.pushfont('bold')
	def end_bold(self, attrs): self.popfont()

	def bgn_italic(self, attrs): self.pushfont('italic')
	def end_italic(self, attrs): self.popfont()

	def bgn_fixed(self, attrs): self.pushfont('fixed')
	def end_fixed(self, attrs): self.popfont()

	def bgn_smaller(self, attrs): self.pushsize(self.size - 1)
	def end_smaller(self, attrs): self.popsize()

	def bgn_bigger(self, attrs): self.pushsize(self.size + 1)
	def end_bigger(self, attrs): self.popsize()

	def bgn_underline(self, attrs): self.pushfont(self.font + ' underline')
	def end_underline(self, attrs): self.popfont()

	def bgn_center(self, attrs): self.pushjust('c')
	def end_center(self, attrs): self.popjust()

	def bgn_flushleft(self, attrs): self.pushjust('l')
	def end_flushleft(self, attrs): self.popjust()

	def bgn_flushright(self, attrs): self.pushjust('r')
	def end_flushright(self, attrs): self.popjust()

	def bgn_indent(self, attrs):
		self.pushleft(self.leftindent + self.stl.indentstep)
	def end_indent(self, attrs): self.popleft()

	def bgn_rightindent(self, attrs):
		self.pushright(self.rightindent + self.stl.indentstep)
	def end_rightindent(self, attrs): self.popright()

	def bgn_outdent(self, attrs):
		self.pushleft(self.leftindent - self.stl.indentstep)
	def end_outdent(self, attrs): self.popleft()

	def bgn_rightoutdent(self, attrs):
		self.pushright(self.rightindent - self.stl.indentstep)
	def end_rightoutdent(self, attrs): self.popright()

	def bgn_subscript(self, attrs): self.pushfont(self.font + ' subscript')
	def end_subscript(self, attrs): self.popfont()

	def bgn_superscript(self, attrs):
		self.pushfont(self.font + ' superscript')
	def end_superscript(self, attrs): self.popfont()

	bgn_heading = ignore_bgn
	end_heading = ignore_end

	bgn_footing = ignore_bgn
	end_footing = ignore_end

	def bgn_excerpt(self, attrs):
		self.fmt.flush()
		self.pushfont('fixed')
	def end_excerpt(self, attrs):
		self.popfont()
		self.fmt.flush()

	def bgn_signature(self, attrs): self.fmt.flush()
	def end_signature(self, attrs): self.fmt.flush()

	def bgn_paragraph(self, attrs): self.fmt.flush()
	def end_paragraph(self, attrs): self.fmt.flush()


class NullStylesheet:

	indentstep = 4

	def makefont(font, size):
		if not font: f = 'r'
		else: f = font[0]
		if size > 0: f = string.upper(f)
		return f


def test():
	import sys
	import fmt
	import time
	if sys.argv[1:]: file = sys.argv[1]
	else: file = 'demo.rich'
	data = open(file, 'r').read()
	t0 = time.time()
	if sys.argv[2:]:
		fmtr = fmt.NullFormatter()
	else:
		fmtr = fmt.FunnyFormatter(sys.stdout, 79)
	p = FormattingParser(fmtr, NullStylesheet)
	p.feed(data)
	p.close()
	fmtr.flush()
	t1 = time.time()
	print
	print '*** Formatting time:', round(t1-t0, 3), 'seconds.'


test()
