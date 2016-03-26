from types import *
from RemoteCallServer import RemoteCallServer
import serverdefs

class TestServer(RemoteCallServer):
	def __init__(self, port):
		RemoteCallServer.__init__(self, port)
		self.EnableAgents()

	def Apply(self, func, args):
		# Called by RemoteCallServer.
		# Derived to let remote client use objects
		# in this namespace
		return apply(func, args)

	def Eval(self, expr):
		# Called by RemoteCallServer.
		# Derived to let remote client use objects
		# in this namespace
		return eval(expr)


def main():
	RemoteCallServer.VERBOSE = 2

	# By default, use system generated port
	port = 0

	# Create socket at port 'port' (or at system generated port
	# if port == 0).
	server = TestServer(port)

	# Register server in Xt dispatcher
	server.XtAddInput()
	server.SendAsAgent(serverdefs.StupidServer)

	print 'OK, waiting on port', server.Port(), '...'

	import Xt
	Xt.MainLoop()

if __name__ == '__main__':
	main()
