#! /usr/local/bin/python

import sys
import os

def main():
	args = sys.argv[1:]
	if not args:
		print 'no files'
		sys.exit(1)
	for file in args:
		print file, '...'
		changed = 0
		lines = open(file, 'r').readlines()
		for i in range(len(lines)):
			line = lines[i]
			if line[-2:] == '\r\n':
				lines[i] = line[:-2] + '\n'
				changed = 1
		if changed:
			print 'rewriting...'
			os.rename(file, file + '~')
			open(file, 'w').writelines(lines)
			print 'done.'
		else:
			print 'no change.'

main()
