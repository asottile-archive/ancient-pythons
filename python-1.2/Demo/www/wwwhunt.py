#! /usr/local/bin/python

# Do a breadth-first search of all HTML documents reachable from a given point.

import sys
import regex
import dbm
import os
import string
import wwwlib
import htmllib

flush = sys.stdout.flush

stripprog = regex.compile('?.*\|#')

stoplist = []

def initstoplist(file):
	f = open(file, 'r')
	while 1:
		line = f.readline()
		if not line: break
		line = string.strip(line)
		if line and line[0] <> '#':
			stoplist.append(regex.compile(line))
	f.close()

def main():
	debug = 0
	while sys.argv[1:] and sys.argv[1] == '-d':
		debug = debug + 1
		del sys.argv[1]
	initstoplist('stop.wwwhunt')
	done = dbm.open('@done', 'rw', 0666)
	errs = dbm.open('@errs', 'rw', 0666)
	stop = dbm.open('@stop', 'rw', 0666)
	todo = dbm.open('@todo', 'rw', 0666)
	othr = dbm.open('@othr', 'rw', 0666)
	for addr in sys.argv[1:]:
		todo[addr] = '(from command line)'
	while 1:
		todolist = todo.keys()
		if not todolist:
			print 'Done!'
			try: os.unlink('@todo.dir')
			except os.error: pass
			try: os.unlink('@todo.pag')
			except os.error: pass
			break
		print 'Next round:', len(todolist), 'addresses to try'
		for addr in todolist:
			bad = 0
			for prog in stoplist:
				if prog.search(addr) >= 0:
					bad = 1
					break
			if bad:
				if debug: print 'Stop!', addr
				stop[addr] = todo[addr]
				del todo[addr]
				continue
			if debug: print 'Fetching', addr, '...',; flush()
			try:
				data = wwwlib.get_document(addr)
				if debug: print 'ok.'; flush()
			except wwwlib.BadAddress, msg:
				if not debug: print addr, ':',
				print msg; flush()
				errs[addr] = todo[addr] + '\t' + msg
				del todo[addr]
				continue
			if debug: print 'Parsing ...',; flush()
			p = htmllib.CollectingParser()
			p.feed(data)
			p.close()
			if debug: print 'ok.', p.title; flush()
			data = todo[addr]
			if p.title: data = data + '\t' + p.title
			done[addr] = data
			for href in p.anchors:
				if debug > 2: print 'Original:', href
				i = stripprog.search(href)
				if i >= 0:
					href = href[:i]
				if not href:
					if debug > 2: print 'Local:', href
					continue
				href = wwwlib.full_addr(addr, href)
##				if href[:5] <> 'http:':
##					if debug > 1: print 'Not http:', href
##					othr[href] = addr
##					continue
				if href in todolist:
					if debug > 1:
						print 'In todolist:', href
					continue
				bad = 0
				for prog in stoplist:
					if prog.search(href) >= 0:
						bad = 1
						break
				if bad:
					if debug > 1: print 'Stop:', href
					stop[href] = addr
					continue
				if todo.has_key(href):
					if debug > 1: print 'In todo:', href
					continue
				if done.has_key(href):
					if debug > 1: print 'In done:', href
					continue
				if debug > 1: print 'New:', href
				todo[href] = addr
			del todo[addr]


main()
