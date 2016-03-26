"""RemoteCall - Execute python statements in remote application.

DESCRIPTION
The RemoteCall is a class for sending calls to other Python applications.
Remote calls are one of

	*  arbitrary expression
	*  function call (i.e. anything you can 'apply' arguments on)
	*  attribute assignment (setattr(obj, attr, value))

Values transferred across the wire are marshalled using the 'pickle' module,
which means not only builtin data types (integers, lists, tuples, etc) can
be transferred, but also user defined classes.

Server side exceptions are reraised on the client side with the original
value, unless the exception value contains unsupported values (see below).

SEE ALSO
Agent.py - A framework for building agent-based applications.

AUTHOR
Daniel Larsson, dlarsson@sw.seisy.abb.se
"""

__version__ = '1.0'

from socket import socket, AF_INET, SOCK_STREAM
from RemoteCalldefs import *

error = 'RemoteCall.error'

class RemoteCall:
	"See module documentation."

	def __init__(self, host=0, port=0):
		# Arguments:
		#   host	name of remote host
		#   port	socket port of remote application
		self._host_   = host
		self._port_   = port

	def Exec(self, call):
		"""Executes 'call', which is a string of python commands, 
		on a remote application. Exceptions in the remote application
		due to the call are propagated to the caller.
		"""
		return self._rpc_(`(EXEC, call)`)

	def Call(self, call, *args):
		"""Executes 'call', which is a string of python commands, 
		on a remote application. Exceptions in the remote application
		due to the call are propagated to the caller.
		"""
		return unpicklify(self._rpc_(`(CALL, (call, picklify(args)))`))

	def Setattr(self, obj, attr, value):
		"""Sets the attribute 'attr', in object 'obj' (which is a string
		referring to a remote object), to 'value'. Exceptions in the remote
		application due to the assignment are propagated to the caller.
		"""
		return self._rpc_(`(SETATTR, (obj, attr, picklify(value)))`)

	def Eval(self, expr):
		"""Executes 'expr', which is a python expression in string form,
		in a remote application. The value of the expression is
		returned to the caller. Exceptions in the remote application
		due to the call are propagated to the caller.
		"""
		return unpicklify(self._rpc_(`(EVAL, expr)`))


	# Private methods:
	def _rpc_(self, rpc):
		sock = socket(AF_INET, SOCK_STREAM)
		sock.connect(self._host_, self._port_)
		sock.send(rpc)

		try:
			value = eval(sock.makefile('r').read())
		except:
			# Could not parse response
			raise error, rpc+': Invalid return value'

		# The result is returned as a 2-tuple, where the first
		# element is None if everything went ok. In case of an
		# error the first element is the exception name and the
		# second the exception value.
		# 
		# NOTE: Exceptions are identified by the exception object's
		# id, not the contents of the string (of course). In Python
		# releases prior to 1.2, exceptions are always strings, and
		# I assume here that the contents of the string is equal to
		# the name of the exception itself. If this assumption is
		# false, there is no way of catching the exception :(.
		#
		# NOTE II: In the face of Python 1.2, this whole scheme will
		# need to be readdressed, since exceptions can not only be
		# string objects but class objects also. There is no support
		# for pickling classes however.
		# (Is this correct? Isn't it instance objects instead of
		# classes?)
		if value[0]:
			try:
				exc = eval(value[0])
			except:
				exc = value[0]
			raise exc, value[1]
		else:
			return value[1]
