# A more powerful formatter class.

# XXX Should change again -- the d_* functions should be methods of a
# separate object passed at init() time, not of a derivced class...


class AbstractFormatter:
	#
	# Font interface functions.  Override these to change the font
	# interface.  (Defaults are for a character cell device.)
	#
	def d_setfont(self, font):
		pass
	#
	def d_textwidth(self, text):
		return len(text)
	#
	def d_baseline(self):
		return 0
	#
	def d_lineheight(self):
		return 1
	#
	# Output interface function.  Override this to define how
	# characters are actually output.
	#
	def d_text(self, (h, v), text):
		pass
	#
	# Initialize a formatter instance.
	# Pass the left, top, right coordinates of the drawing space
	# as arguments.  (There is no bottom argument -- the bottom of
	# the text is computed as a side effect of formatting it.)
	#
	def init(self, left, top, right):
		self.left = left	# Left margin, variable
		self.leftmargin = left	# Left margin, fixed
		self.right = right	# Right margin, variable
		self.rightmargin = right # Right margin, fixed
		self.v = top		# Top of current line
		self.center = 0
		self.justify = 0
		self.setfont('')	# Default font
		self._reset()		# Prepare for new line
		return self
	#
	# Reset for start of fresh line.
	#
	def _reset(self):
		self.boxes = []		# Boxes and glue still to be output
		self.sum_width = 0	# Total width of boxes
		self.sum_space = 0	# Total space between boxes
		self.sum_stretch = 0	# Total stretch for space between boxes
		self.max_ascent = 0	# Max ascent of current line
		self.max_descent = 0	# Max descent of current line
		self.avail_width = self.right - self.left
		self.hang_indent = 0
	#
	# Set the current font, and compute some values from it.
	#
	def setfont(self, font):
		self.font = font
		self.d_setfont(font)
		self.font_space = self.d_textwidth(' ')
		self.font_ascent = self.d_baseline()
		self.font_descent = self.d_lineheight() - self.font_ascent
	#
	# Set the current justification / centering flags.
	#
	def setjustify(self, flag):
		self.justify = flag
	#
	def setcenter(self, flag):
		self.center = flag
	#
	# Extract the bottom of the text.  Implies a flush.
	#
	def getbottom(self):
		self.flush()
		return self.v
	#
	# Add a word to the list of boxes; first flush if line is full.
	# Space and stretch factors are expressed in fractions
	# of the current font's space width.
	# (Two variations: one without, one with explicit stretch factor.)
	#
	def addword(self, word, spacefactor):
		self.addwordstretch(word, spacefactor, spacefactor)
	#
	def addwordstretch(self, word, spacefactor, stretchfactor):
		width = self.d_textwidth(word)
		if width > self.avail_width:
			self._flush(1)
		space = int(float(self.font_space) * float(spacefactor))
		stretch = int(float(self.font_space) * float(stretchfactor))
		box = (self.font, word, width, space, stretch)
		self.boxes.append(box)
		self.sum_width = self.sum_width + width
		self.sum_space = self.sum_space + space
		self.sum_stretch = self.sum_stretch + stretch
		self.max_ascent = max(self.font_ascent, self.max_ascent)
		self.max_descent = max(self.font_descent, self.max_descent)
		self.avail_width = self.avail_width - width - space
	#
	# Flush current line and start a new one.
	# Flushing twice is harmless (i.e. does not introduce a blank line).
	# (Two versions: the internal one has a parameter for justification.)
	#
	def flush(self):
		self._flush(0)
	#
	def _flush(self, justify):
		if not self.boxes:
			return
		#
		# Compute amount of stretch needed_
		#
		if justify and self.justify or self.center:
			#
			# Compute extra space to fill;
			# this is avail_width plus glue from last box.
			# Also compute available stretch.
			#
			last_box = self.boxes[len(self.boxes)-1]
			font, word, width, space, stretch = last_box
			tot_extra = self.avail_width + space
			tot_stretch = self.sum_stretch - stretch
		else:
			tot_extra = tot_stretch = 0
		#
		# Output the boxes.
		#
		baseline = self.v + self.max_ascent
		h = self.left + self.hang_indent
		if self.center:
			h = h + tot_extra / 2
			tot_extra = tot_stretch = 0
		for font, word, width, space, stretch in self.boxes:
			self.d_setfont(font)
			v = baseline - self.d_baseline()
			self.d_text((h, v), word)
			h = h + width + space
			if tot_extra > 0 and tot_stretch > 0:
				extra = stretch * tot_extra / tot_stretch
				h = h + extra
				tot_extra = tot_extra - extra
				tot_stretch = tot_stretch - stretch
		#
		# Prepare for next line.
		#
		self.v = baseline + self.max_descent
		self.d_setfont(self.font)
		self._reset()
	#
	# Add vertical space; first flush.
	# Vertical space is expressed in fractions of the current
	# font's line height.
	#
	def vspace(self, lines):
		self.vspacepixels(int(lines * self.d_lineheight()))
	#
	# Add vertical space given in pixels.
	#
	def vspacepixels(self, dv):
		self.flush()
		self.v = self.v + dv
	#
	# Set temporary (hanging) indent, for paragraph start.
	# First flush.
	#
	def tempindent(self, space):
		self.flush()
		hang = int(float(self.font_space) * float(space))
		self.hang_indent = hang
		self.avail_width = self.avail_width - hang
	#
	# Set (permanent) left indentation.  First flush.
	#
	def setleftindent(self, space):
		self.flush()
		self.left = self.leftmargin + \
			int(float(self.font_space) * float(space))
		self._reset()
	#
	# Add (permanent) left indentation.  First flush.
	#
	def addleftindent(self, space):
		self.flush()
		self.left = self.left \
			+ int(float(self.font_space) * float(space))
		self._reset()


class WritingFormatter(AbstractFormatter):
	#
	def init(self, fp, linewidth):
		self.fp = fp
		self.lineno, self.colno = 0, 0
		return AbstractFormatter.init(self, 0, 0, linewidth)
	#
	def d_text(self, (h, v), text):
		if '\n' in text:
			raise ValueError, 'no newline allowed in d_text'
		while self.lineno < v:
			self.fp.write('\n')
			self.colno, self.lineno = 0, self.lineno + 1
		if self.colno < h:
			self.fp.write(' ' * (h - self.colno))
		elif self.colno > h:
			self.fp.write('\b' * (self.colno - h))
		self.colno = h
		self.fp.write(text)
		self.colno = h + len(text)


class StdwinFormatter(AbstractFormatter):
	#
	def init(self, d, left, top, right):
		self.d = d
		return AbstractFormatter.init(self, left, top, right)
	#
	def d_text(self, point, text):
		self.d.text(point, text)
	#
	def d_setfont(self, font):
		self.d.setfont(font)
	#
	def d_textwidth(self, text):
		return self.d.textwidth(text)
	#
	def d_baseline(self):
		return self.d.baseline()
	#
	def d_lineheight(self):
		return self.d.lineheight()


class BufferingStdwinFormatter(AbstractFormatter):
	#
	def init(self, left, top, right):
		import stdwin
		self.d = stdwin
		self.buffer = []
		self.curfont = None
		return AbstractFormatter.init(self, left, top, right)
	#
	def d_text(self, point, text):
		self.buffer.append('t', (point, text))
	#
	def d_setfont(self, font):
		if font <> self.curfont:
			self.curfont = font
			self.d.setfont(font)
			self.buffer.append('f', font)
	#
	def d_textwidth(self, text):
		return self.d.textwidth(text)
	#
	def d_baseline(self):
		return self.d.baseline()
	#
	def d_lineheight(self):
		return self.d.lineheight()
	#
	def render(self, d, area):
		(left, top), (right, bottom) = area
		ntop = top - d.lineheight()
		for command, args in self.buffer:
			if command == 't':
				(h, v), text = args
				if v >= bottom:
					break
				if v > ntop and h < right:
					d.text(args)
			else:
				d.setfont(args)
				ntop = top - d.lineheight()


class GLFormatter(AbstractFormatter):
	#
	# NOTES:
	# (1) Use gl.ortho2 to use X pixel coordinates!
	# (2) Call setfont with some font handle immediately after initializing
	#
	def init(self, left, top, right):
		self.fontkey = None
		self.fonthandle = None
		self.fontinfo = None
		self.fontcache = {}
		return AbstractFormatter.init(self, left, top, right)
	#
	def d_text(self, (h, v), text):
		import gl, fm
		gl.cmov2i(h, v + self.fontinfo[6] - self.fontinfo[3])
		fm.prstr(text)
	#
	def d_setfont(self, fontkey):
		if fontkey == '':
			fontkey = 'Times-Roman 12'
		elif ' ' not in fontkey:
			fontkey = fontkey + ' 12'
		if fontkey == self.fontkey:
			return
		if self.fontcache.has_key(fontkey):
			handle = self.fontcache[fontkey]
		else:
			import string
			i = string.index(fontkey, ' ')
			name, sizestr = fontkey[:i], fontkey[i:]
			size = eval(sizestr)
			key1 = name + ' 1'
			key = name + ' ' + `size`
			# NB key may differ from fontkey!
			if self.fontcache.has_key(key):
				handle = self.fontcache[key]
			else:
				if self.fontcache.has_key(key1):
					handle = self.fontcache[key1]
				else:
					import fm
					handle = fm.findfont(name)
					self.fontcache[key1] = handle
				handle = handle.scalefont(size)
				self.fontcache[fontkey] = \
					self.fontcache[key] = handle
		self.fontkey = fontkey
		if self.fonthandle <> handle:
			self.fonthandle = handle
			self.fontinfo = handle.getfontinfo()
			handle.setfont()
	#
	def d_textwidth(self, text):
		return self.fonthandle.getstrwidth(text)
	#
	def d_baseline(self):
		return self.fontinfo[6] - self.fontinfo[3]
	#
	def d_lineheight(self):
		return self.fontinfo[6]
