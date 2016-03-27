# Qualify.py main module for (large) number factorization program
# Copyright (c) 1992 by Jan-Hein B\"uhrman & Niels T. Ferguson


# Pseudoprimes are first tested by Rabin-Miller to the bases 3 2 5 7 11 13
# after that a number of tests to random bases are done. This parameter governs
# the probability of a composite slipping through these ADDITIONAL tests
log2_pprime_prob = 0			# prob of error _after_ sfpp(2,...,13)

pprime_trial_limit = 10000		# Trial division limit for is_pprime
crack_trial_limit = 10000		# Limit for factoring
pollard_rho_maxiters = 1000		# max # iterations per polynomial
pollard_rho_maxpolys = 10		# max # polynomials to try

import simplerandom
random_function = simplerandom.simplerandom('').random


from sparcearr import sparcearr, SparceArr
import smallprimes
import rabin_miller
import pollardrho
from assert import assert

from mpz import *

UNKNOWN = 0
PRIME = 1
PROBPRIME = 2
COMPOSITE = 3
PROBFACTORED = 4
FACTORED = 5

error = 'qualify.error'

status_syms = sparcearr(\
	  (UNKNOWN, 'UNKNOWN'), \
	  (PRIME, 'PRIME'), \
	  (PROBPRIME, 'PROBPRIME'), \
	  (COMPOSITE, 'COMPOSITE'), \
	  (PROBFACTORED, 'PROBFACTORED'), \
	  (FACTORED, 'FACTORED'), \
	  )

def range_random(lwb, upb):
	return lwb + random_function(upb - lwb)

class FactorList(SparceArr):

	def __init__(self, *pairs):
		SparceArr.__init__(self, [], [])
		apply(self.update, pairs)

	def update(self, *pairs):
		for (fnb, exp) in pairs:
			key = fnb.n
			if key not in self.keys():
				self[key] = fnb, exp
			else:
				pres_fnb, pres_exp = self[key]
				self[key] = pres_fnb, pres_exp + exp

	def addfactor(self, f):
		self.update((f, 1), )


def factorlist(*pairs):
	return apply(FactorList, pairs)
			

class Fnum:

	def __init__(self, n, status, factorfreebound):
		self.n = n
		assert(status in status_syms.keys())
		self.status = status
		self.factors = factorlist()
		self.factorfreebound = factorfreebound


	def newstatus(self, s):
		# print 'newstatus(' + `self` + ', ' + status_syms[s] + ')'
		if s == self.status:
			print 'WARNING, newstatus(' + \
				  `self` + ', ' + status_syms[s] + ')'
			return
		if s == UNKNOWN:
			raise error, 'newstatus(UNKNOWN)'
		elif s == PRIME:
			assert(self.status in (UNKNOWN, PROBPRIME))
		elif s == COMPOSITE:
			assert(self.status in (UNKNOWN, PROBPRIME))
			if self.status == PROBPRIME:
				print 'Pseudoprime ', `self.n`, \
					  'turns out to be composite!'
		elif s == PROBPRIME:
			assert(self.status in (UNKNOWN, ))
		elif s == FACTORED:
			assert(self.status in \
				  (UNKNOWN, COMPOSITE, PROBFACTORED))
		elif s == PROBFACTORED:
			assert(self.status in (UNKNOWN, COMPOSITE))
		else:
			raise error, 'Newstatus = ' + `s` + \
				  '; oldstatus = ' + `self.status`
		self.status = s
		
		
	def trial(self, bound):
		if bound <= self.factorfreebound:
			return
		n = self.n
		primes = smallprimes.minbound(bound)
		i = smallprimes.ge_index(self.factorfreebound)
		for p in primes[i:]:
			if p > bound:
				break
			q, r = divmod(n, p)
			if q < p:
				self.factorfreebound = p + 1
				break
			if not r:
				self.factorfreebound = p
				self.foundfactors([fnum(p, PRIME), \
					  fnum(q, UNKNOWN, p)])
				return
		else:
			self.factorfreebound = bound
		if self.factorfreebound * self.factorfreebound > n:
			self.newstatus(PRIME)
			self.proof = 'factorfreebound > sqrt(n)'
		return

	def rabin_miller( self ):
		for b in (3, 2, 5, 7, 11, 13):
			# print 'Miller test, base = ' + `b` ,
			t = rabin_miller.miller_test(b, self.n)
			# print `t`
			if t:
				break
		else:
			for k in range(log2_pprime_prob/2):
				b = range_random(2, self.n-1)
				# print 'Miller test, base = ' + `b` ,
				t = rabin_miller.miller_test(b, self.n)
				# print `t`
				if t:
					break;
		if not t:
			self.newstatus(PROBPRIME)
			return
		if len(t) == 2:
			self.foundfactors(t)
		else:
			self.newstatus(COMPOSITE)
			self.proof = 'Miller-rabin, base = ' + `b`

	def pollardrho(self, maxiters, maxpolys):
		t = pollardrho.try_pollard_rho(\
			  self.n, maxiters, maxpolys, random_function)
		if len(t) > 0:
			self.foundfactors( [ fnum(t[0]), fnum(self.n/t[0]) ])
				
	def foundfactors(self, list):
		# print 'Found factors ' + `list` + ' of ' + `self`
		prod = 1
		for i in list:
			##print 'Found factor ' + `i.n` + ' of number '+ `self.n`
			prod = prod * i.n;
			self.factors.addfactor(i)
		assert(prod == self.n)
		if( self.status != COMPOSITE ):
			self.newstatus(COMPOSITE)


	def selfridge(self):
		# first we factor n-1
		
		n = self.n
		assert(n > 2)
		self.nminus1 = fnum(n-1, COMPOSITE)
		t = self.nminus1.factor()
	
		# for each prime p dividing n-1, we find a number b such that
		# b^(n-1) = 1 (mod n)
		# b^((n-1)/p) != 1 (mod n)
		# I include a miller test, so that this loop wil always end
		# print 'Selfridge primality proving...'

		proof = []
		for p in self.nminus1.factors.keys():
			while 1:
				b = range_random(2, n-1)
				# check for first 
				t = rabin_miller.miller_test(b, n)
				# Handle case that miller finds composite
				if t:
					if len(t) == 2:
						self.foundfactors(t)
					else:
						self.newstatus(COMPOSITE)
						self.proof = 'Miller-rabin,' \
							  + ' base = ' + `b`
						return 0
				if powm(b, (n-1)/p, n) != 1:
					proof.append( (p, b) )
					break
		self.newstatus(PRIME)
		self.proof = 'Selfridge: ' + `proof`
		
	def crack(self):
		if self.status != COMPOSITE:
			print 'Some fool tries to crack a non-composite number'
		if len(self.factors) > 0:
			return
		self.trial(crack_trial_limit)
		if len(self.factors) > 0:
			return

		# pollard rho
		self.pollardrho(pollard_rho_maxiters, pollard_rho_maxpolys)
		if len(self.factors) > 0:
			return
			
		# Out of algo's. Continue with best one
		print 'I\'m desparate, clutching at straws...'
		self.pollardrho(100000, 5)
		if len(self.factors) > 0:
			return
			
		print 'Sorry, could not find any factor of ' + `self.n`

		raise error, 'Unable to factor number'
		
	def is_prime(self):
		# returns when it is known if n is prime or not

		# print 'Determining status of ' + `self`
		# first we check that we are at least pseudoprime
		if self.status not in (PROBPRIME, UNKNOWN):
			return(self.status == PRIME)
			
		if self.status == UNKNOWN and not self.is_pprime():
			return 0

		if self.status == PRIME:
			return 1

		assert(self.status == PROBPRIME)
		self.selfridge()

		return (self.status == PRIME)

	def is_pprime( self ):
		# returns when it is known if n is a probprime or not
		# print 'Determining probstatus of ' + `self`
		if self.status != UNKNOWN:
			return self.status in (PRIME, PROBPRIME)
		# print 'Trial division...'
		self.trial(pprime_trial_limit)
		if self.status != UNKNOWN:
			return self.status in (PRIME, PROBPRIME)
		self.rabin_miller()
		if self.status != UNKNOWN:
			return self.status in (PRIME, PROBPRIME)
		raise error, 'Rabin_Miller left status UNKNOWN'

	def _factor(self, test_def_method):
		# factors untill all factors are at least probprimes
		if test_def_method(self):
			return [self.n]

		self.crack()
		##print 'Just cracked ' + `self.n`
		done = (self.status == PRIME)
		while not done:
			done = 1
			for k in self.factors.keys():
				f, e = self.factors[k]
				if not test_def_method(f):
					done = 0
					del self.factors[k]
					f.crack()
					if test_def_method(f):
						break
					for fk in f.factors.keys():
						ff, fe = f.factors[fk]
						self.factors.update(\
							  (ff, fe*e), )
		s = FACTORED
		for k in self.factors.keys():
			if self.factors[k][0].status == PROBPRIME:
				s = PROBFACTORED
				break
		self.newstatus(s)
		return self.factors

	def factor(self):
		return self._factor(Fnum.is_prime)

	def pfactor(self):
		return self._factor(Fnum.is_pprime)
		
	def __repr__(self):
		return 'fnum(' + `self.n` + ', ' + status_syms[self.status] \
			  + ', ' + `self.factorfreebound` + ')'

	
def fnum(n, *rest):
	if len(rest) == 2:
		return Fnum(n, rest[0], rest[1])
	if len(rest) == 1:
		return Fnum(n, rest[0], 2)
	elif len(rest) != 0:
		raise TypeError, 'fnum(.): too many arguments (>3)'
	return Fnum(n, UNKNOWN, 2) 
