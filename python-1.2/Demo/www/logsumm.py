#! /usr/local/bin/python

import sys
import getopt
import string

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], '')
	except getopt.error, msg:
		sys.stdout = sys.stderr
		print msg
		sys.exit(2)
	file = '/ufs/guido/src/www/Log-inet'
	if args: file = args[0]
	if file == '-':
		fp = sys.stdin
	else:
		try:
			fp = open(file, 'r')
		except IOError, msg:
			sys.stdout = sys.stderr
			print file, ': I/O Error:', msg
			sys.exit(1)
	process(fp)

def process(fp):
	per_file = {}
	per_host = {}
	per_day = []
	errors_per_day = []
	last_day = None
	lineno = 0
	while 1:
		line = fp.readline()
		if not line: break
		lineno = lineno + 1
		words = string.split(line)
		if len(words) < 5:
			print 'line', lineno, ': bad line :', line,
			continue
		[month, day, time, year] = words[:4]
		# Count requests per day
		if (year, month, day) <> last_day:
			do_header = 0
			if last_day:
				print last_day[1], last_day[2], len(per_day),
				if errors_per_day:
					print '(', len(errors_per_day),
					print 'errors )',
				print
				if (year, month) <> last_day[:2]:
					print
					print '****** Summary of',
					print last_day[1], last_day[0],
					print '******'
					show_per_file(per_file)
					show_per_host(per_host)
					per_file = {}
					per_host = {}
					do_header = 1
			else:
				do_header = 1
			if do_header:
				print
				print '****** Requests per day in',
				print month, year, '******'
			per_day = []
			errors_per_day = []
			last_day = (year, month, day)
		if len(words) == 8 and words[4] == 'sending' and \
			  words[6] == 'to':
			file = words[5]
			host = words[7]
			per_day.append(time, file, host)
			if not per_file.has_key(file):
				per_file[file] = []
			per_file[file].append(year, month, day, time, host)
			if not per_host.has_key(host):
				per_host[host] = []
			per_host[host].append(year, month, day, time, file)
		else:
			errors_per_day.append(time, words[4:])
	print
	print '****** Summary of',
	print last_day[1], last_day[0],
	print '******'
	show_per_file(per_file)
	show_per_host(per_host)

def show_per_file(per_file):
	print '====== top scoring files ======'
	files = per_file.keys()
	score = []
	for file in files:
		score.append(len(per_file[file]), file)
	score.sort()
	score.reverse()
	for count, file in score:
		print string.rjust(`count`, 3), file,
		(year, month, day, time, host) = per_file[file][0]
		print '(', day, realname(host),
		if len(per_file[file]) > 1:
			(year, month, day, time, host) = per_file[file][-1]
			print day,
		print ')'

def show_per_host(per_host):
	print '====== top scoring hosts ======'
	hosts = per_host.keys()
	score = []
	for host in hosts:
		score.append(len(per_host[host]), host)
	score.sort()
	score.reverse()
	for count, host in score:
		print string.rjust(`count`, 3), realname(host),
		(year, month, day, time, file) = per_host[host][0]
		print '(', day, file,
		if len(per_host[host]) > 1:
			(year, month, day, time, file) = per_host[host][-1]
			print day,
		print ')'

def realname(host):
	try:
		import nis
	except ImportError:
		return host
	try:
		response = nis.match(host, 'hosts.byaddr')
		words = string.split(response)
		return words[1]
	except nis.error:
		return host

main()
