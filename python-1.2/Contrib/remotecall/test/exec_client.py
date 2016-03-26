#/usr/local/bin/python
#
# Simple client using RemoteCall interface to make a server do some maths.
#

import sys
from RemoteCall import RemoteCall

if len(sys.argv) <= 2:
	port = eval(sys.argv[1])
else:
	host = eval(sys.argv[1])
	port = eval(sys.argv[2])

print "Do some remote calculations:"
remcall = RemoteCall('138.221.22.200', port)
print "Ok, remote call connection established."

n = 1000
print "\nLet the server calculate sum(8/((4n+1)(4n+3))), when n =", n


pi = remcall.Eval("reduce(lambda sum, n: sum+8.0/((4*n+1)*(4*n+3)), range(%d), 0)" % n)
print "Result =", pi
