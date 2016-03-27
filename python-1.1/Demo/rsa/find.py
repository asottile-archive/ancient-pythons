from qualify import fnum

def makeprime(mod, rf):
	half = mod / 2
##	print 'Trying',
	while 1:
		candidate = half + rf(half)
##		print candidate,
		if fnum(candidate).is_prime():
##			print
			return candidate
def makepprime(mod, rf):
	half = mod / 2
##	print 'Trying',
	while 1:
		candidate = half + rf(half)
##		print candidate,
		if fnum(candidate).is_pprime():
##			print
			return candidate
			
