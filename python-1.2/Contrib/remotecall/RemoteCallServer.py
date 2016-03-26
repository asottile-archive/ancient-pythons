"""RemoteCallServer - Handle remote calls from other python applications

DESCRIPTION
The RemoteCallServer is a class for handling remote calls from other Python
applications. Remote calls are one of

	*  arbitrary expression
	*  function call (i.e. anything you can 'apply' arguments on)
	*  attribute assignment (setattr(obj, attr, value))

Values transferred across the wire are marshalled using the 'pickle' module,
which means not only builtin data types (integers, lists, tuples, etc) can
be transferred, but also user defined classes.

After an incomming value is unpickled, but before it is further processed
(e.g. sent as arguments to a function) one can optionally process it with
a 'before' method. Likewise, before pickling the results and sending them back
an after method may massage it. The main reason for this facility is to
implement 'Agents'.

AGENTS
Agents are objects that acts as local representatives of remote objects.
Agents are also known in other systems as proxys, ambassadors, and other
names. Agents are useful for objects that use facilities local to the server
that might not be available at the client (e.g. they might interface to
an application with python embedded).

By installing agent support, and telling the RemoteCallServer object what
objects and/or classes not to send over the wire, all such objects appearing
in results from a RemoteCall will automatically be converted to agents.
An agent sent as an argument is likewise translated automatically to the
corresponding server object.

PROTOCOL
A remote request is a 2-tuple where the first element indicates whether
the second element is to be considered an expression, a call, an assignment
or a record control request.

If the request is an expression or a call, it is evaluated and if the evaluation
succeeds the tuple '(None, result)' is returned. In the case an exception is
raised the tuple '(exc_type, exc_value)' is returned instead.

If the request is an assignment it is executed and if successfull the tuple
'(None, None)' is returned. In the case an exception is raised the tuple
'(exc_type, exc_value)' is returned instead.

NOTES
When enabling agent support, currently all transferred tuples will be copied,
whether they contain agents or not.

AUTHOR
Daniel Larsson, dlarsson@sw.seisy.abb.se
"""

__version__ = '1.0'

import posix
from types import *
from RemoteCalldefs import *
from Agent import Agent


class RemoteCallServer:
	"""RemoteCallServer - Handle remote calls from other python applications.
	Further documentation on module."""

	_agent_refs_ = {}

	# Verbose mode for printing trace and debug messages.
	VERBOSE		= 0

	def __init__(self, port=0):
		"""Arguments:
		port	port to listen for requests. If 0 is given
			the system will generate a suitable port.
		"""
		from socket import socket, SOCK_STREAM, AF_INET, gethostname, gethostbyname
		self._sock_ = socket(AF_INET, SOCK_STREAM)
		self._addr_ = gethostbyname(gethostname())
		# Guido told me he had to replace self._addr_ with ''
		# below. Why?
		self._sock_.bind('', port)
		self._sock_.listen(1)

		# Get the actual port number (in case port arg was 0)
		if port == 0:
			port = self._sock_.getsockname()[1]

		# Initialize members
		self._port_      = port	# socket port nr
		self._makeagents_= []	# List of objects/classes which
					# shouldn't be transferred over
					# the wire, but send agents instead.
		self._after_	 = self._default_after_
		self._before_	 = self._default_before_

	# ---  Public methods  ---
	def Port(self):
		"Return the port number I am using."
		return self._port_

	def fileno(self):
		"Return file descriptor of the socket I am listening on."
		return self._sock_.fileno()

	def SetBefore(self, before):
		"Set user defined 'before' method"
		self._before_ = before

	def SetAfter(self, after):
		"Set user defined 'after' method"
		self._after_ = after

	def EnableAgents(self):
		"""Sets up the server to handle agents. This function sets
		the 'before' and 'after' methods."""
		self.SetAfter(self.MakeAgents)
		self.SetBefore(self.ReplaceAgents)

	def SendAsAgent(self, obj):
		"""'obj' or instances of 'obj' should not be sent over the wire
		"as is", but rather as agents (i.e. the object stays at the
		server and the client gets a proxy object, here called agent)"""
		self._makeagents_.append(obj)

	def MakeAgents(self, result):
		"""Replaces objects that should be sent as agents with a corresponding
		agent.
		
		This method is normally used internally when agent support
		is enabled. You can use this method directly if you for some
		reason do not want general agent support but only for some
		selected cases."""

		resultType = type(result)
		if resultType == ListType:
			result = map(self.MakeAgents, result)
		elif resultType == DictionaryType:
			newresult = {}
			for ix in result.keys():
				newresult[ix] = self.MakeAgents(result[ix])
			result = newresult
		elif resultType == TupleType:
			result = tuple(map(self.MakeAgents, result))
		elif result in self._makeagents_ \
		  or (hasattr(result, '__class__') and result.__class__ in self._makeagents_):
			RemoteCallServer._agent_refs_[id(result)] = result
			agent = Agent('RemoteCallServer._agent_refs_['+`id(result)`+']', self._addr_, self._port_, 0)
			result = agent
			if self.VERBOSE > 1:
				print 'Agent created :', result
		return result

	def ReplaceAgents(self, value):
		"""Replaces agents in 'value' with the actual objects they
		refer to.
		
		This method is normally used internally when agent support
		is enabled. You can use this method directly if you for some
		reason do not want general agent support but only for some
		selected cases."""
		valueType = type(value)
		if valueType == ListType:
			value = map(self.ReplaceAgents, value)
		elif valueType == DictionaryType:
			for ix in value.keys():
				value[ix] = self.ReplaceAgents(value[ix])
		elif valueType == TupleType:
			value = tuple(map(self.ReplaceAgents, value))
		elif hasattr(value, '__class__') and value.__class__ == Agent:
			value = self.Eval(value.remoteObject())
		return value		


	# ---  Evaluating and executing python code  ---
	
	def Eval(self, expr):
		"""This is the function which must evaluate the expression sent
		from a remote node. To be able to call application specific
		functions it is necessary to inherit from this class and
		override the eval method so that it executes in the right name
		space. By default they execute here, which means almost nothing
		is visible."""
		
		return eval(expr)

	def Exec(self, code):
		"""This is the function which executes the code sent
		from a remote node. To be able to call application specific
		functions it is necessary to inherit from this class and
		override the eval method so that it executes in the right name
		space. By default they execute here, which means almost nothing
		is visible."""
		
		exec code


	# ---  Process incomming requests  ---
	
	def ReceiveRequestCB(self):
		"""Callback to call when a message is received on the socket.
		If 'AddInput' is used you don't have to bother with this
		function. If, however you use some other synchronization
		mechanism, this is the function to call to handle requests."""

		conn, addr = self._sock_.accept()
		if self.VERBOSE:
			print 'Connected by ', addr

		try:
			from FCNTL import O_NONBLOCK
			mode, request = eval(conn.recv(10240, O_NONBLOCK))
		except:
			import sys
			result = sys.exc_type, sys.exc_value
		else:
			if self.VERBOSE > 1:
				print 'Received :', request

			try:
				# Default return value
				result = (None, None)

				if mode == CALL:
					method, args = request
					result = None, self._call_(method, args)
				elif mode == EVAL:
					result = None, self._eval_expr_(request)
				elif mode == EXEC:
					result = None, self.Exec(request)
				elif mode == SETATTR:
					obj, attr, value = request
					result = None, self._setattr_(obj, attr, value)
				else:
					raise 'Mode error', mode

			except:
				import sys
				result = sys.exc_type, sys.exc_value

		if self.VERBOSE > 1:
			print 'Result :', result

		conn.send(`result`)
		conn.close()

		if self.VERBOSE:
			print 'OK, wait for next...'


	# ---  Utility functions for using Xt or Stdwin dispatching on fileno  ---

	def XtAddInput(self):
		"Register myself in Xt dispatcher."
		import Xt
		from Xtdefs import XtInputReadMask

		Xt.AddInput(self.fileno(), XtInputReadMask, self._XtCB, None)

	def _XtCB(self, dummy, fd, id):
		self.ReceiveRequestCB()

	def StdwinAddInput(self):
		"Register myself in Stdwin dispatcher."
		import mainloop
		mainloop.registerfd(self.fileno(), 'r', self._StdwinCB)

	def _StdwinCB(self, fd, mode):
		self.ReceiveRequestCB()


	# ---  Private methods  ---

	def _call_(self, method, args):
		m = self.Eval(method)
		return picklify(self._after_(apply(m, self._before_(unpicklify(args)))))

	def _eval_expr_(self, expr):
		return picklify(self._after_(self.Eval(expr)))

	def _setattr_(self, obj, attr, value):
		return picklify(setattr(self.Eval(obj), attr, self._before_(unpicklify(value))))

	def _default_before_(self, value):
		return value

	_default_after_ = _default_before_
