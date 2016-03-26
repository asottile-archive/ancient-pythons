#! /usr/local/bin/python

# RSA cryptographic key maintenance

# (0) All numers are stored in text files as Python Long constants
# (1) Your own secret key is in $HOME/.rsa_secret_key (this file has mode 0600)
# (2) Your public key is in $HOME/.rsa_public_key
# (3) The public key of any user on your system can be read from their $HOME
# (4) In addition, other public keys can be read from the private file
#     $HOME/.rsa_database, where each line contains a name (no whitespace),
#     some whitespace, and that user's public key

# Usage:
# rsa            print your own public key
# rsa user ...   print the public key for the given user(s)
# rsa -a         print the public keys for all users in your database
# rsa -c         create a new public key; prompts for a random seed
# rsa -s         print your secret key

# XXX (4) is not yet implemented; rsa -a lists the keys of all local users

NBITS = 512

import sys
import getopt
import os
import string

PKEYFILE = '.rsa_public_key'
SKEYFILE = '.rsa_secret_key'

sys.path.append('/ufs/guido/src/python/new/Demo/rsa')

from rsakeys import makersaset, default_pk
from simplerandom import simplerandom
from mpz import powm, mpz

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'acs')
	except getopt.error, msg:
		sys.stderr.write(str(msg) + '\n')
		usage()
		sys.exit(2)
	all = 0
	create = 0
	secret = 0
	for opt, arg in opts:
		if opt == '-a': all = 1
		if opt == '-c': create = 1
		if opt == '-s': secret = 1
	if create: createskey()
	if secret: listskey()
	if all: listallskeys()
	if args:
		for user in args: listpkey(user)
	elif not create and not secret and not all and not args:
		listpkey('')

def usage():
	sys.stdout = sys.stderr
	print 'usage:'
	print 'rsa\t\tlists your own public key'
	print 'rsa -s\t\tlists your own secret key'
	print 'rsa -n\t\tcreates a new secret key for you'
	print 'rsa user ...\tlists the public key for user(s)'

def listskey():
	try:
		key = getskey()
	except KeyError, msg:
		sys.stderr.write('Can\'t get secret key (' + str(msg) + ')\n')
		return
	print key

def listpkey(user):
	try:
		key = getpkey(user)
	except KeyError, msg:
		if not user:
			try:
				user = os.path.basename(findhome(user))
			except:
				user = '???'
		sys.stderr.write( \
		  'Can\'t get private key for ' + user + ' (' + msg + ')\n')
		return
	if user: print user + ':',
	print key

def listallkeys():
	import pwd
	for entry in pwd.getpwall():
		user = entry[0]
		try:
			key = getkey(user)
		except KeyError:
			continue
		print user + ':', key

def createskey():
	home = findhome('')
	pkeyfile = os.path.join(home, PKEYFILE)
	skeyfile = os.path.join(home, SKEYFILE)
	print 'Creating new secret/public key pair for', os.path.basename(home)
	while 1:
		seed = raw_input('Please enter a random seed string: ')
		seed = string.strip(seed)
		if len(seed) > 5: break
		print 'Please try something a bit longer!'
	rf = simplerandom(seed).random
	print 'Calculating...'
	n, sk = makersaset(NBITS, rf)
	if os.path.exists(skeyfile) or os.path.exists(pkeyfile):
		print 'Backing up old files...'
		try:
			os.rename(skeyfile, skeyfile + '~')
		except os.error:
			pass
		try:
			os.rename(pkeyfile, pkeyfile + '~')
		except os.error:
			pass
	print 'Writing ' + pkeyfile + ' (mode -rw-r--r--)'
	save_umask = None
	try:
		save_umask = os.umask(022)
		f = open(pkeyfile, 'w')
		f.write(str(long(n)) + '\n')
		f.close()
		dummy_umask = os.umask(077)
		print 'Writing ' + skeyfile + ' (mode -rw-------)'
		f = open(skeyfile, 'w')
		f.write(str(long(sk)) + '\n')
		f.close()
	finally:
		if save_umask <> None:
			dummy_umask = os.umask(save_umask)
	print 'Done.'

def getpkey(*args):
	if args:
		if len(args) > 1: raise TypeError, 'too many args'
		user = args[0]
	else:
		user = ''
	home = findhome(user)
	file = os.path.join(home, PKEYFILE)
	try:
		f = open(file, 'r')
	except IOError:
		raise KeyError, 'file open error'
	try:
		return long(eval(string.strip(f.read())))
	except:
		raise KeyError, 'bad data in file'

def getskey():
	home = os.path.expanduser('~')
	skeyfile = os.path.join(home, SKEYFILE)
	try:
		f = open(skeyfile, 'r')
	except IOError:
		raise KeyError, 'can\'t open file'
	try:
		sk = long(eval(string.strip(f.read())))
	except:
		raise Keyerror, 'bad data in file'
	return sk

def findhome(user):
	return os.path.expanduser('~' + user)

if os.path.basename(sys.argv[0]) in ('rsa', 'rsa.py'):
	main()

