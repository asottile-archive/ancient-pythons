#
# $Id: engine.py,v 1.1 1993/12/17 14:34:41 guido Exp $
#

from report import *

from merge import gluetimes

class Engine:
	#
	#
	#
	def __init__(self, g):
		self.df = g.data	# the data-generator function
		self.datalen = g.datalen
		self.stock = '\0' * self.datalen
		self.instock = 0
	#
	#
	#
	def expand(self, nbytes):
		reportnl('Engine().expand(' + `nbytes` + ')')
		#
		# first use up the data that we still have in stock
		#
		if nbytes < self.instock:
			# it's even less than that
			return self._keeprest(nbytes)
		result = self.stock[self.datalen-self.instock:]
		nbytes = nbytes - self.instock
		#
		# self.instock should actually set to zero now, but
		# we won't use it for a short period
		#
		quot, rem = divmod(nbytes, self.datalen)
		result = result + gluetimes(quot, self.df)
		if rem:
			self.stock = self.df()
			self.instock = self.datalen
			return result + self._keeprest(rem)
		self.instock = 0
		return result
	#
	#
	#
	def _keeprest(self, nbytes):
		startval = self.datalen - self.instock
		self.instock = self.instock - self.datalen
		return self.stock[startval:startval+nbytes]

def engine(g):
	reportnl('engine(' + `g` + ')')
	return Engine(g)
