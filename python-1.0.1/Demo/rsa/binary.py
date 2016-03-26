#
# $Id: binary.py,v 1.1 1993/12/17 14:34:41 guido Exp $
#
# binary: try to compress some unknown type to a universal binary type
#           in python this can be stored in the native string type.
#	    String or a ``as-number'' > 0 must be given
#           A string itself will not be compressed.

from mpz import mpz

def tobinary(arg):
	#return mpz(arg).binary()	# implement short-cut (speed concerns)
	if type(arg) == type(''):
		return arg
	return mpz(arg).binary()

def topaddedbinary(arg, l):
	result = tobinary(arg)
	diff = l - len(result)
	if diff < 0:
		raise ValueError, 'topaddedbinary(): l parameter too small'
	return '\0' * diff + result

def frombinary(arg):
	return mpz(arg)
