# Implementation of pollard-rho factorization method
# Copyright (c) 1992 by Jan-Hein B\"uhrman & Niels T. Ferguson
#

from mpz import *

def one_pollard_rho(n, start, c, maxiterations):
	# print 'Pollard-Rho: n = ' + `n` + ', f(x) = x^2 + ' + `c`
	x1, x2, r, prod, terms = start, (start*start + c) % n, 1, 1, 0
	while terms < maxiterations:
		for j in range(r):
			x2, prod, terms = \
				  (x2 * x2 + c) % n, \
				  prod * ((x1 + n - x2) % n) % n, \
				  terms + 1
			if not (terms & 0x0f) :
				g = gcd(n, prod)
				if g > 1 :
					return [g]
				if g == 0 :
					return []
				prod = 1
				# print terms
		x1, r = x2, r+r
		for j in range(r):
			x2 = (x2*x2 + c) % n
	return []
		
def try_pollard_rho(n, maxiters, maxpolys, rf):
	for i in range(maxpolys):
		c = 1 + rf(n - 3)
		r = one_pollard_rho(n, 1 + rf(n - 1), c, maxiters)
		if len(r) > 0:
			break
	return r
