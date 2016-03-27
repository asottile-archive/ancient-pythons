#! /usr/local/bin/python

import sys
import string
import dbm

def main():
	dbnames = ['done', 'todo', 'stop', 'errs', 'othr']
	dbd = {}
	for dbname in dbnames[:]:
		try:
			dbd[dbname] = dbm.open('@' + dbname, 'r', 0)
		except dbm.error, msg:
			print '@' + dbname, ':', msg
			dbnames.remove(dbname)
	for addr in sys.argv[1:]:
		if addr in dbnames:
			db = dbd[addr]
			print 'Database', addr, 'has', len(db), 'Entries'
			for key in db.keys():
				print key
				result = db[key]
				parts = string.splitfields(result, '\t')
				label = 'from'
				for p in parts:
					print label, p
					label = ' '*len(label)
			continue
		print addr
		for dbname in dbnames:
			db = dbd[dbname]
			if db.has_key(addr):
				result = db[addr]
				parts = string.splitfields(result, '\t')
				for p in parts:
					print dbname, p
					dbname = ' '*len(dbname)

main()
