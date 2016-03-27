#! /usr/local/bin/python

import sys, marshal, regex, os, string, getopt, wwwlib

PLACES = '.wwwplaces'

def main():
	places_file = PLACES
	if os.environ.has_key('HOME'):
		places_file = os.path.join(os.environ['HOME'], places_file)
	#
	wantbyaddr = wantbytitle = 0
	#
	opts, args = getopt.getopt(sys.argv[1:], 'atp:')
	for o, a in opts:
		if o == '-p':
			places_file = a
		if o == '-a':
			wantbyaddr = 1
		if o == '-t':
			wantbytitle = 1
	#
	if not wantbyaddr and not wantbytitle:
		wantbytitle = 1
	#
	types = []
	progs = []
	for arg in args:
		if not arg: continue
		if arg[0] == '!': type = '!'; arg = arg[1:]
		else: type = ''
		progs.append(type, regex.compile(string.lower(arg)))
		if type not in types: types.append(type)
	#
	f = open(places_file, 'r')
	places = marshal.load(f)
	f.close()
	#
	bytitle = []
	byaddr = []
	#
	for addr in places.keys():
		title, exits = places[addr]
		title = string.strip(title)
		if progs:
			lctitle = string.lower(title)
			lcaddr = string.lower(addr)
			good = 0
			bad = 0
			for type, prog in progs:
				if prog.search(lctitle) >= 0 or \
				   prog.search(lcaddr) >= 0:
					if type == '!':
						bad = 1
					else:
						good = 1
					break
			if bad:
				continue
			if not good:
				if '' in types:
					continue
		if not title: title = '(untitled)'
		bytitle.append(title, addr)
		byaddr.append(addr, title)
	#
	bytitle.sort()
	byaddr.sort()
	#
	print '<TITLE>Places you have visited</TITLE>'
	if args:
		print 'Search keywords:'
		for arg in args:
			print arg
		print '<P>'
	if wantbytitle:
		print '<H1>Places you have visited, by title</H1>'
		for title, addr in bytitle:
			print '<A HREF=' + addr + '>'+ title + '</A>', \
			      addr, '<P>'
	if wantbyaddr:
		print '<H1>Places you have visited, by address</H1>'
		for addr, title in byaddr:
			print '<A HREF=' + addr + '>' + addr + '</A>', \
			      title, '<P>'


main()
