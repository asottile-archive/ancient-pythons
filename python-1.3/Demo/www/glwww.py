import sys
import html
import gl, GL, DEVICE
from Formatter import *


class GLStylesheet:
	stdfont = 'Helvetica 12'
	fixedfont = 'Courier 12'
	boldfont = 'Helvetica-Bold 12'
	bigboldfont = 'Helvetica-Bold 14'
	verybigboldfont = 'Helvetica-Bold 18'


def main():
	import T
	if not sys.argv[1:]:
		print 'usage: www file'
		sys.exit(2)
	file = sys.argv[1]
	try:
		fp = open(file, 'r')
		data = fp.read()
		fp.close()
	except IOError, msg:
		print file, ':', msg
		sys.exit(1)

	W, H = 600, 600
	gl.foreground()
	gl.prefsize(W, H)
	wid = gl.winopen('glwww')
	gl.color(GL.WHITE)
	gl.clear()
	gl.ortho2(0, W, H, 0)
	gl.color(GL.BLACK)
	T.TSTART()
	fmt = GLFormatter().init(5, 0, W-5)
	p = html.FormattingParser().init(fmt, GLStylesheet)
	p.feed(data)
	p.close()
	T.TSTOP()
	gl.wintitle(p.title)
	import time
	time.sleep(5)

main()
