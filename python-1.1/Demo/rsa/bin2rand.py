
from report import *
from binary import *

success_rate = 10

class Bin2Rand:
	#
	#
	#
	def __init__(self, ef):
		self.ef = ef		# pointer to the expand function
		self.n = None
		self.highest_multiple = None
		self.l = None
	#
	#
	#
	def random(self, n):
		if n != self.n:
			self._newlimit(n)
		return self._random()
	#
	#
	#
	def _newlimit(self, n):
		reportnl('Bin2Rand()._newlimit(' + `n` + ')')
		if n <= 0:
			raise ValueError, 'bin2rand._newlimit(n): n <= 0'
		self.n = n
		self.l = len(tobinary(n))
		ceil = frombinary('\0' * self.l + '\1')
		quot, rem = divmod(ceil, n)
		if rem != 0 and quot < success_rate:
			reportnl('Bin2Rand()._newlimit: 1 byte more')
			self.l = self.l + 1
			ceil = ceil << 8
			quot, rem = divmod(ceil, n)
		self.highest_multiple = ceil - rem  # should be eq. to  quot*n
	#
	#
	#
	def _random(self):
		reportnl('Bin2Rand()._random()')
		while 1:
			result = frombinary(self.ef(self.l))
			if result < self.highest_multiple:
				break
			reportnl(('Bin2Rand()._random(): retrying, result', result))
		return result % self.n

def bin2rand(ef):
	reportnl('bin2rand(' + `ef` + ')')
	return Bin2Rand(ef)
