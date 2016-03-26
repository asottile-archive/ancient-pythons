# Demonstration of the RSA cryptosystem.  This lets you use a public
# channel (one where everybody can read what you send) to send
# messages encrypted using a public encryption key, but which can
# only be decrypted by who knows the secret decryption key.
#
# The security of the method comes from the fact that it is hard to
# factorize the product of two large primes -- and we can always use
# larger primes if the enemy buys a faster computer.
#
# It works as follows (in laymen's terms, and without proof):
# - Let n be a large number, the modulus (e.g. about 512 bits).
# - Let sk be the secret key and pk be the public key.
# - Let plaintext be the message we want to encode, a number less than n.
# - Let crypttext be plaintext to the power pk modulo n.
# Then crypttext to the power sk modulo n equals plaintext again.
#
# Actually, n is the product of two (pseudo-)primes n1 and n2, pk is a
# (small) prime, and sk is the inverse of pk mod (n1-1)*(n2-1), i.e.
# pk*sk == 1 mod (n1-1)*(n2-1).  Then x**(pk*sk) == x (mod n) for all x.
# This is the Chinese remainder theorem -- it actually only works for
# real primes!
#
# The hard problem is coming up with suitable primes; our
# implementation only uses pseudo-primes (numbers that aren't
# obviously non-primes, given a suitable pseudo-primality test).
#
# Reference:
#
# RL Rivest, A Shamir, L Adleman.  A method for obtaining digital
# signatures and public-key cryptosystems.  CACM 21(2):120-126,
# February, 1978.


# Import some functions
from rsakeys import makersaset, default_pk
from simplerandom import simplerandom
from mpz import powm
from T import TSTART, TSTOP

# Make a random function (the seed determines the secret key computed!)
rf = simplerandom('<YOUR SEED HERE...>').random

# Use the default public key
pk = default_pk

# Choose a random n and secret key (this can take from 5-50 seconds
# on an R4000 processor at 50 MHz!).  Note that this is deterministic
# if you don't vary the seed for the random function above
TSTART()
n, sk = makersaset(512, rf)
TSTOP('makersaset')
print n
print sk

# Choose a random plaintext message to test the algorithms
TSTART()
plaintext = rf(n)
TSTOP('plaintext')
print plaintext

# Encrypt the plaintext
TSTART()
crypttext = powm(plaintext, pk, n)
TSTOP('crypttext')
print crypttext

# Decrypt the crypttext
TSTART()
testvalue = powm(crypttext, sk, n)
TSTOP('testvalue')
print testvalue

# The decrypted crypttext should be the same as the original plaintext
if testvalue != plaintext:
	raise 'FATAL', 'RSA implementation failed!'
