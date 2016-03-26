# Distributed Audio Library.

# This module provides an interface that is (almost) the same as that
# of SGI's audio library, but which interfaces to the audio device of
# the machine indicated by the $DISPLAY environment variable, rather
# than the machine on which the process is running.  This means e.g.
# that if you have a shell in a window on a remote machine and you run
# a program that plays some sound, the sound comes out of the speaker
# on the machine whose display and keyboard you are using rather than
# the machine on which the shell happens to be running.

# It is possible to take an existing Python program that uses the
# audio library and make a very small local change to it so that it
# will be using dal instead of al, *if* $DISPLAY does not point to the
# local machine.  This requires that you import dal and call
# dal.takeover() *before* importing al.  For instance:
#   import dal
#   dal.takeover()
#   import al
# This should be put in the main program before importing any other
# modules that might also import al.  The takeover() function does
# nothing when $DISPLAY indicates the local host (in any disguise, as
# long as the IP numbers match).

# It is also possible to use dal explicitly by opening a connection
# and using methods of this connection:
#   import dal
#   conn = dal.openconn()
#   port = conn.openport(...)
# The openconn() function has an optional argument indicating the host
# to connect to.

# A feature of openconn() and takeover() is that if $DISPLAY is not
# set or points to a bad host, it does not fall back to using the
# local host but raise an exception.  This means that programs run
# from a non-windowed environment (e.g. a remote login from a modem)
# will fail to produce sound rather than annoy the person sitting at
# the machine's display.  An exception is also raised when the remote
# DAL server cannot be contacted.

# It should be noted that this is only a prototype implementation.
# Not all functionality is implemented, and all functions cause a
# server roundtrip.  Applications that are critical to timing will
# notice that remote audio operations are slower than their local
# counterparts and precise synchronization with other remote I/O may
# not be possible.

# CAVEAT: The server does not do any authorization checking.  Once you
# start the DAL server, anyone with a DAL client can manipulate your
# audio device.  You have been warned!

# XXX One possible optimization would be to open a separate TCP
# connection for a port, to be used for writesamps and readsamps.  At
# least for writesamps this would avoid the roundtrip.  (For readsamps
# it would still require the roundtrip, but it would save some copying
# time.)


import sys
sys.path.append('/ufs/guido/src/python/new/Demo/rpc')
import socket
import AL
import al
import rpc
from dalxdr import *


Error = 'dal.Error'			# Exception


class Config:

	def __init__(self):
		self.queuesize = 100000
		self.width = AL.SAMPLE_16
		self.channels = AL.STEREO
		self.sampfmt = AL.SAMPFMT_TWOSCOMP
		self.floatmax = 1.0

	def setqueuesize(self, queuesize):
		self.queuesize = int(queuesize)
	def getqueuesize(self):
		return self.queuesize

	def setwidth(self, width):
		self.width = int(width)
	def getwidth(self):
		return self.width

	def setchannels(self, channels):
		self.channels = int(channels)
	def getchannels(self):
		return self.channels

	def setsampfmt(self, sampfmt):
		self.sampfmt = int(sampfmt)
	def getsampfmt(self):
		return self.sampfmt

	def setfloatmax(self, floatmax):
		self.floatmax = float(floatmax)
	def getfloatmax(self):
		return self.floatmax


class Port:
	def __init__(self, conn, name, config, index):
		self.conn = conn
		self.name = name
		self.config = config
		self.index = index
	def closeport(self):
		self.conn.call_12(self.index)
		self.index = -1

	def getfd(self):
		return None
	fileno= getfd

	def getfilled(self):
		return self.conn.call_13(self.index)
	def getfillable(self):
		return self.conn.call_14(self.index)

	def readsamps(self, nsamps):
		return self.conn.call_15(self.index, nsamps)
	def writesamps(self, buffer):
		self.conn.call_16(self.index, buffer)

	def getfillpoint(self):
		return self.conn.call_17(self.index)
	def setfillpoint(self, fillpoint):
		self.conn.call_18(self.index, fillpoint)

	def getconfig(self):
		config_flat = self.conn.call_19(self.index)
		queuesize, width, channels, sampfmt, floatmax = config_flat
		c = al.newconfig()
		c.setqueuesize(queuesize)
		c.setwidth(width)
		c.setchannels(channels)
		c.setsampfmt(sampfmt)
		c.setfloatmax(floatmax)
		return c
	def setconfig(self, c):
		config_flat = c.getqueuesize(), c.getwidth(), \
			      c.getchannels(), c.getsampfmt(), c.getfloatmax()
		self.conn.call_20(self.index, config_flat)

	def getstatus(self, params):
		params[:] = self.conn.call_21(self.index, params)


class DALClient(rpc.TCPClient):

	def __init__(self, host):
		rpc.TCPClient.__init__(self, host, 0x25924127, 1)
	def addpackers(self):
		self.packer = DALPacker()
		self.unpacker = DALUnpacker('')

	def call_1(self, dev): # queryparams
		return self.make_call(1, dev, \
			  self.packer.pack_int, \
			  self.unpacker.unpack_params)
	def call_2(self, dev, params): # getparams
		return self.make_call(2, (dev, params), \
			  self.packer.pack_int_params, \
			  self.unpacker.unpack_params)
	def call_3(self, dev, params): # setparams
		return self.make_call(3, (dev, params), \
			  self.packer.pack_int_params, \
			  None)
	def call_4(self, dev, descr): # getname
		return self.make_call(4, (dev, descr), \
			  self.packer.pack_int_int, \
			  self.unpacker.unpack_string)
	def call_5(self, dev, descr): # getdefault
		return self.make_call(5, (dev, descr), \
			  self.packer.pack_int_int, \
			  self.unpacker.unpack_int)
	def call_6(self, dev, descr): # getminmax
		return self.make_call(6 (dev, descr), \
			  self.packer.pack_int_int, \
			  self.unpacker.unpack_int_int)

	def call_11(self, name, mode, config): # openport
		return self.make_call(11, (name, mode, config), \
			  self.packer.pack_openport, \
			  self.unpacker.unpack_int)
	def call_12(self, i): # closeport
		return self.make_call(12, i, \
			  self.packer.pack_int, \
			  None)
	def call_13(self, i): # getfilled
		return self.make_call(13, i, \
			  self.packer.pack_int, \
			  self.unpacker.unpack_int)
	def call_14(self, i): # getfillable
		return self.make_call(14, i, \
			  self.packer.pack_int, \
			  self.unpacker.unpack_int)
	def call_15(self, i, n): # readsamps
		return self.make_call(15, (i, n), \
			  self.packer.pack_readsamps, \
			  self.unpacker.unpack_string)
	def call_16(self, i, buffer): # writesamps
		return self.make_call(16, (i, buffer), \
			  self.packer.pack_writesamps, \
			  None)
	def call_17(self, i): # getfillpoint
		return self.make_call(17, i, \
			  self.packer.pack_int, \
			  self.unpacker.unpack_int)
	def call_18(self, i, fillpoint): # setfillpoint
		return self.make_call(18, (i, fillpoint), \
			  self.packer.pack_int_int, \
			  None)
	def call_19(self, i): # getconfig
		return self.make_call(19, i, \
			  self.packer.pack_int, \
			  self.unpacker.unpack_config)
	def call_20(self, i, config_flat): # setconfig
		return self.make_call(20, (i, config_flat), \
			  self.packer.pack_setconfig, \
			  None)
	def call_21(self, i, params): # getstatus
		return self.make_call(21, (i, params), \
			  self.packer.pack_int_params, \
			  self.unpacker.unpack_params)

	def newconfig(self):
		return Config()

	def queryparams(self, dev):
		return self.call_1(dev)
	def getparams(self, dev, params):
		params[:] = self.call_2(dev, params)
	def setparams(self, dev, params):
		self.call_3(dev, params)
	def getname(self, dev, descr):
		return self.call_4(dev, descr)
	def getdefault(self, dev, descr):
		return self.call_5(dev, descr)
	def getminmax(self, dev, descr):
		return self.call_6(dev, descr)

	def openport(self, name, mode, *args):
		if len(args) > 1: raise TypeError, 'too many args'
		if args:
			c = args[0]
		else:
			c = self.newconfig()
		config_flat = c.getqueuesize(), c.getwidth(), \
			      c.getchannels(), c.getsampfmt(), c.getfloatmax()
		index = self.call_11(name, mode, config_flat)
		if index < 0:
			raise Error, 'openport failed'
		return Port(self, name, c, index)


def takeover():
	import os
	import sys
	import string
	if not sys.modules.has_key('_local_al'):
		sys.modules['_local_al'] = sys.modules['al']
	host = defaulthost()
	if host:
		sys.modules['al'] = openconn(host)


def openconn(*args):
	if len(args) > 1: raise TypeError, 'too many args'
	if args:
		host = args[0]
	else:
		host = defaulthost()
	return DALClient(host)


def defaulthost():
	import os
	import string
	if not os.environ.has_key('DISPLAY'):
		raise Error, '$DISPLAY not set'
	display = os.environ['DISPLAY']
	words = string.splitfields(display, ':')
	if len(words) <> 2:
		raise Error, 'bad $DISPLAY format'
	[host, number] = words
	if not host or host == 'unix':
		return ''		# Implied local display
	# Compare host IP addresses, not hostname, because of aliases
	try:
		iphost = socket.gethostbyname(host)
	except socket.error:
		raise Error, 'bad host in $DISPLAY'
	iplocalhost = socket.gethostbyname(socket.gethostname())
	if iphost == iplocalhost:
		return ''		# Explicit local display
	return iphost


def test():
	import sys
	import os
	import time
	if sys.argv[1:]: file = sys.argv[1]
	else: file = '/usr/local/sounds/aiff/1999_intro.aiff'
##	else: file = '/usr/local/sounds/aiff/Ah_Ha!.aiff'
	f = open(file, 'r')
	f.seek(64) # Skip header bytes
	conn = openconn()
	c = conn.newconfig()
	c.setqueuesize(100000)
##	c.setchannels(AL.MONO)
	p = conn.openport('test', 'r', c)
	try:
		buffer = p.readsamps(1000)
	finally:
		p.closeport()
	p = conn.openport('test', 'w', c)
	p.writesamps(buffer)
	try:
		while 1:
			buffer = f.read(50000)
			if not buffer:
				break
			p.writesamps(buffer)
		while p.getfilled() > 0:
			time.sleep(0.1)
	finally:
		p.closeport()


def test1():
	import time
	conn = openconn()
##	p = conn.openport('test1', 'r', c)
	t0 = time.time()
	for i in range(100):
		conn.call_0()
	t1 = time.time()
	print round(t1-t0, 3), 'sec.'
