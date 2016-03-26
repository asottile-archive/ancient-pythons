"""Agents provide a simple mechanism to implement distributed applications.
An agent is a client side representative of a server object. Through the
agent it is possible to access attributes and execute methods on the server.
Communication with servers are done via sockets.

The server object can be any kind of python object having attributes (e.g.
instance, class, module).

Server side exceptions are reraised on the client side with the original
value, unless the exception value contains unsupported values (see below).

Normally, agents are created by clients to represent a known server object.
Sometimes, however, server methods return objects that should not be moved
to the client process, but rather stay in the server. In such cases it is
possible to ask the client to create an agent for the returned object instead.
The server then keeps a reference to the object to avoid garbage collection.
This reference is removed when the client removes his agent. The value to
return from the server in this case is an agent identification string which
contains a reference to the object in string form (the reference is prefixed
by a "magic" string to make it distinguishable from normal return values).

EXAMPLE
To implement an agent for the server object

	class Server:
		def __init__(self):
			self.anAttr = 47

		def method(sel, arg1, arg2):
			....

	server = Server()

you must create an agent for it:

	from Agent import Agent

	server = Agent('host.name.here', port)

	# get an attribute
	print server.anAttr
	
	# Call a method
	server.method('To be or not to be...', 'do be do be do')

CAVEAT
The types of values that can be transferred over the net is limited to:
None, integers, long integers, floating point numbers, strings, tuples,
lists, dictionaries and code objects. (the elements of tuples, lists and
dictionaries must of course also fall into above categories).

AUTHOR
Daniel Larsson, dlarsson@sw.seisy.abb.se
"""

__version__ = '1.0'

from RemoteCall import RemoteCall
from types import *

error = 'Agent.error'

class Agent:

	def __init__(self, remote=0, host=0, port=0, do_config=1):
		"""Arguments:
		  remote	name of the remote object
		  host		name of host where remote object resides
		  port		socket port of application holding remote object
		  byServer	Agent created by server (only used internally)
		"""

		# Since this class has a '__setattr__' method, we must go
		# via the '__dict__' attribute to fool python.
		if remote:
			if not (host and port):
				raise error, 'You must give host and port of remote object'
			self.__dict__['_remote_']   = remote
			self.__dict__['_remcall_']  = RemoteCall(host, port)
			self.__dict__['_byServer_'] = 0
			if do_config:
				self._config_()
		else:
			self.__dict__['_remote_']   = None
			self.__dict__['_remcall_']  = None
			
	def __repr__(self):
		return self._remote_+' at %s:%d' % (self._remcall_._host_, self._remcall_._port_)

	__str__ = __repr__

	def __getinitargs__(self):
		return ()

	def __getstate__(self):
		return self._remote_, self._remcall_

	def __setstate__(self, state):
		self.__dict__['_remote_']   = state[0]
		self.__dict__['_remcall_']  = state[1]
		self.__dict__['_byServer_'] = 1

	def __getattr__(self, attr):
		"""All variable read accesses (i.e. agent.attr) result in
		a call to this function, unless 'attr' is found in
		the agent object itself. This function will get 'attr'
		from the remote server object."""

		result = self._remcall_.Eval(self._remote_+'.'+attr)
		self._config_agents_(result)
		return result

	def __setattr__(self, attr, value):
		"""All variable write accesses (i.e. agent.attr = 4) result in
		a call to this function, unless 'attr' is found in
		the agent object itself. This function will set 'attr'
		in the remote server object."""

		return self._remcall_.Setattr(self._remote_, attr, value)

	def remoteObject(self):
		return self._remote_

	def Remove(self):
		"""Remove agent (i.e. remove all method objects and if the
		agent was created by server, also remove the book keeping
		reference to the server object from the server).
		The reason we have an explicit remove service is because all
		method objects have references to the agent so no garbage
		collection will occur if we simply delete the reference to
		the agent."""

		if self._byServer_:
			self._remcall_.Exec('del '+self._remote_)
		for name in self.__dict__.keys():
			object = self.__dict__[name]
			if type(object) == InstanceType and object.__class__ == self.Method:
				del self.__dict__[name]


	class Method:
		# This class represents a method on the agent.

		def __init__(self, agent, method):
			"""Arguments:
			   agent	the agent instance the method shall use
			   method	name of the method (string)"""

			self._agent_ = agent
			self._method_ = method

		def __call__(self, *args):
			"""This 'magic' method enables calling instances as if
			they were functions. It will perform a remote procedure
			call on the server object the agent is connected to."""

			result = apply(self._agent_._remcall_.Call,
				  (self._agent_._remote_+'.'+self._method_,)+args)
			self._agent_._config_agents_(result)
			return result

	# Private methods:
	def _config_(self):
		"""Tries to create Method objects (see below) to match the
		connected server object's interface. This method checks
		the server's __class__ attribute (if it has any) and the
		object itself."""

		try:
			class_obj = self._remote_+'.__class__'
			# Pick up the object's class' methods, if any
			self._configobj_(class_obj)

			# Pick up the object's class' bases' methods
			self._config_bases_(class_obj)				
		except: pass

		self._configobj_(self._remote_)

	def _configobj_(self, object):
		"""Tries to create Method objects (see below) to match "object"'s
		interface. This method assumes the object has a '__dict__'
		attribute."""

		# Find all functions in 'object'
		f_type = 'type('+object+'.__dict__[f])'
		filter_fun = 'lambda f:'+f_type+' == FunctionType or '+ \
			     f_type+' == BuiltinFunctionType or '+ \
			     f_type+' == UnboundMethodType'
		funs_cmd = 'filter('+filter_fun+','+object+'.__dict__.keys())'

		# Send the filter function to server.
		funs = self._remcall_.Eval(funs_cmd)

		# Create method objects for all attributes not starting with '_'
		for fun in funs:
			if fun[0] != '_':
				self.__dict__[fun] = Agent.Method(self, fun)


	def _config_bases_(self, class_obj):
		"""Traverse the inheritance hierarchy of the class object
		and pick up inherited methods."""

		bases = self._remcall_.Eval('len('+class_obj+'.__bases__)', 0)
		for base in range(bases):
			# Add methods from base
			base_obj = class_obj+'.__bases__['+`base`+']'
			self._configobj_(base_obj)
			# Add methods from base's bases
			self._config_bases_(base_obj)

	def _config_agents_(self, value):
		"If 'value' contains agents, configure them."

		valueType = type(value)
		if valueType == ListType:
			for item in value:
				self._config_agents_(item)
		elif valueType == DictionaryType:
			for item in value.values():
				self._config_agents_(item)
		elif valueType == TupleType:
			for item in value:
				self._config_agents_(item)
		elif hasattr(value, '__class__') and value.__class__ == Agent:
			value._config_()
