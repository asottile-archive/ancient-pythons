# Implementation of the Rabin-Miller test
# Copyright (c) 1992 by Jan-Hein B\"uhrman & Niels T. Ferguson


from assert import assert
from mpz import *
from qualify import log2_pprime_prob

def miller_test(base, n):
	# first we check that we have an odd number larger then 10
	# print 'Rabin-Miller test, n = ' + `n` + ', base = ' + `base`
	assert( (n & 1 and n > 10) )
	k, q = 0, n-1
	while (q & 1) == 0:
		k, q = k+1, q >> 1
	# print `k`, `q`
	# print `base`, `q`, `n`
	t, pt = powm(base, q, n), 0
	if t == 1:
		# test to this base return 'probably prime'
		return []
	nm1 = n-1
	while k > 0 and t != nm1:
		tp, t, k = t, (t*t) % n, k-1
	if k > 0 and t == nm1:
		return []
	f = gcd((t - pt) % n, n)
	if 1 < f < n:
		print 'MILLER TEST FOUND FACTOR: n = ' + `n` + \
			  '; base = ' + `base` 
		return [f, n/f]
	else:
		return [n]
