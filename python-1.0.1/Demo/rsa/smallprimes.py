# smallprimes.py Module for generating small primes
# Copyright (c) 1992 by Jan-Hein B\"uhrman & Niels T. Ferguson

from math import sqrt
import sys

initial_primes_bound = 1

def minbound( k ):
	global bound, primes
	if k <= bound:
		return primes
	if k > 2*bound:
		# just a quick heuristic
		bound = k
		primes = None
		primes = eratosthenes(k)
	else:
		for i in range(bound | 1, k, 2):
			for d in primes:
				q, r = divmod(i, d)
				if q < d:
					primes.append(i)
					break
				if not r:
					break
	return primes

def ge_find(lwb, upb, n):
	if lwb == upb - 1:
		return lwb
	h = (upb + lwb) / 2
	if primes[h] <= n:
		return ge_find(h, upb, n)
	else:
		return ge_find(lwb, h, n)
	
def ge_index(n):
	return ge_find(0, len(primes), n)
	
def eratosthenes(upb):
	# list is from 0 to max (inclusive)
	# in list, i maps to real number 2i+1
	print 'Generating small primes list...',
	sys.stdout.flush()
	max = (upb-1) / 2
	rootlimit = int(sqrt(float(max / 2)))
	r = range(max+1)
	r[0] = None
	#print r
	
	for pi in r:
		if pi:
			#print  2*pi+1
			if pi > rootlimit:
				break
			i = 2 * (pi*pi + pi)
			p = pi + pi + 1
			while i <= max:
				r[i]= None
				i = i + p
			#print r
	res = [2]
	for pi in r:
		if pi:
			res.append(pi + pi + 1)
	print
	return res
	

primes = [2] #eratosthenes(initial_primes_bound)
bound =  3    #initial_primes_bound


		
	

	
	
			
				
		
