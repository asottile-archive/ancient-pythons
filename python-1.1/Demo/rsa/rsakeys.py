
from find import makepprime
from mpz import gcd, divm

default_pk = 7

# makersaset(RSASIZE, RF, PK=DEFAULT_PK)
#
#    makes an RSA keyset. RSASIZE is the size in bits, minimal value should
#    be around 512 bits.  RF is a function object that, when called as RF(N),
#    should return a random number 0 <= X < N.  Normally, PK is a small
#    prime.
#
#    returns a tuple (MODULUS, SK), where modulus is the RSA modulus of the
#    requested size, and SK complementary key of PK.
#
def makersaset(RSAsize, rf, *rest):

	if rest:
		pk, = rest
	else:
		pk = default_pk


	n1size = RSAsize/2 - 1

	while 1:
		n1 = makepprime(1L << n1size, rf)
		if gcd(n1-1, pk) == 1:
			break


	while 1:
		n2 = makepprime((1L << RSAsize) / n1, rf)
		if gcd(n2-1, pk) == 1:
			break
			
	n = n1 * n2			# this is the RSA modulus
	
	sk = divm(1, pk, (n1-1)*(n2-1))

	return n, sk
