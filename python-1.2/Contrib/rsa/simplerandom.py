#
# a truly simple random number generator, returns mpz-numbers
#

from report import *

from md5gen import md5gen
from engine import engine
from bin2rand import bin2rand

def simplerandom(seed):
	reportnl('simplerandom(' + `seed` + ')')
	return bin2rand(engine(md5gen(seed)).expand)
