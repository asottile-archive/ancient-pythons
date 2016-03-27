import sys, os, string, stdwin
from stdwinevents import *
from Formatter import *


def TSTART():
	global t0, t1
	u, s = os.times()[:2]
	t0 = u + s

def TSTOP():
	global t0, t1
	u, s = os.times()[:2]
	t1 = u + s
	sys.stderr.write(`t1-t0` + ' secs.\n')


def openfile():
	if sys.argv[1:] and sys.argv[1] <> '-':
		return open(sys.argv[1], 'r')
	else:
		return sys.stdin


def feedfile(fp, fmt):
	while 1:
		line = fp.readline()
		if not line:
			break
		words = string.split(line)
		if not words:
			fmt.vspace(1)
		else:
			for word in words:
				fmt.addword(word, 1)
	fmt.flush()


def makecalls(fp, FMT):
	calls = []
	while 1:
		line = fp.readline()
		if not line:
			break
		words = string.split(line)
		if not words:
			calls.append(FMT.vspace, 1)
		else:
			for word in words:
				calls.append(FMT.addword, word, 1)
	calls.append((FMT.flush,))
	return calls


def feedcalls(calls, fmt):
	self = (fmt,)
	for call in calls:
		apply(call[0], self + call[1:])


def test():
	fp = openfile()
	TSTART()
	fmt = WritingFormatter().init(sys.stdout, 72)
	feedfile(fp, fmt)
	TSTOP()


def wtest():
	fp = openfile()
	w = stdwin.open('wtest')
	while 1:
		type, win, detail = stdwin.getevent()
		if type == WE_CLOSE:
			break
		if type == WE_DRAW:
			TSTART()
			left, top = 0, 0
			right, bottom = w.getwinsize()
			d = w.begindrawing()
			fmt = StdwinFormatter().init(d, left, top, right)
			fp.seek(0)
			feedfile(fp, fmt)
			d.close()
			TSTOP()
	w.close()


def wwtest():
	fp = openfile()
	TSTART()
	calls = makecalls(fp, StdwinFormatter)
	TSTOP()
	w = stdwin.open('wwtest')
	while 1:
		type, win, detail = stdwin.getevent()
		if type == WE_CLOSE:
			break
		if type == WE_DRAW:
			TSTART()
			left, top = 0, 0
			right, bottom = w.getwinsize()
			d = w.begindrawing()
			fmt = StdwinFormatter().init(d, left, top, right)
			feedcalls(calls, fmt)
			d.close()
			TSTOP()
	w.close()


def wwwtest():
	fp = openfile()
	TSTART()
	calls = makecalls(fp, StdwinFormatter)
	TSTOP()
	w = stdwin.open('wwwtest')
	TSTART()
	left, top = 0, 0
	right, bottom = w.getwinsize()
	fmt = BufferingStdwinFormatter().init(left, top, right)
	feedcalls(calls, fmt)
	bottom = fmt.getbottom()
	w.setdocsize(0, bottom)
	TSTOP()
##	for x in fmt.buffer: print x
	while 1:
		type, win, detail = stdwin.getevent()
		if type == WE_CLOSE:
			break
		if type == WE_SIZE:
			width, height = w.getwinsize()
			if width <> right:
				TSTART()
				left, top = 0, 0
				right, bottom = w.getwinsize()
				fmt = BufferingStdwinFormatter(). \
					init(left, top, right)
				feedcalls(calls, fmt)
				bottom = fmt.getbottom()
				w.setdocsize(0, bottom)
				TSTOP()
		if type == WE_DRAW:
			TSTART()
			d = w.begindrawing()
			fmt.render(d, detail)
			d.close()
			TSTOP()
	w.close()




def gltest():
	import gl, fm
	gl.foreground()
	W, H = 1000, 800
	gl.prefsize(W, H)
	wid = gl.winopen('gltest')
	gl.ortho2(0, W, H, 0)
	gl.color(7)
	gl.clear()
	gl.color(0)
	fp = openfile()
	TSTART()
	fmt = GLFormatter().init(5, 0, W)
	feedfile(fp, fmt)
	fmt.flush()
	TSTOP()
	import time
	time.sleep(5)


#test()
#wtest()
#wwtest()
#wwwtest()
#gltest()
