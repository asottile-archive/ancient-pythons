


from report import *

from md5 import md5
_len = len(md5('').digest())

class Md5Gen:
	#
	#
	#
	def __init__(self, seed):
		self.datalen = _len
		self.md5 = md5(seed)
	#
	#
	#
	def data(self):
		reportnl('md5gen.data()')
		onedigest = self.md5.digest()
		self.md5.update(onedigest)
		return onedigest

def md5gen(seed):
	reportnl('md5gen(' + `seed` + ')')
	return Md5Gen(seed)
