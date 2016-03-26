# Server for Distributed Audio Library.

# Start this manually when you log in after starting your X server.

# CAVEAT: The server does not do any authorization checking.  Once you
# start the DAL server, anyone with a DAL client can manipulate your
# audio device.  You have been warned!

# XXX error returns are bogus!


import sys
sys.path.append('/ufs/guido/src/python/new/Demo/rpc')
import al
import AL
import rpc
from dalxdr import *


class DALServer(rpc.TCPServer):

	def __init__(self):
		rpc.TCPServer.__init__(self, '', 0x25924127, 1, 0)
	def addpackers(self):
		self.packer = DALPacker()
		self.unpacker = DALUnpacker('')

	def session(self, connection):
		self.all_ports = []
		try:
			rpc.TCPServer.session(self, connection)
		finally:
			all_ports = self.all_ports
			del self.all_ports
			for p in all_ports:
				if p: p.closeport()
	def getport(self, index):
		if not 0 <= index < len(self.all_ports):
			return None
		return self.all_ports[index]

	def handle_1(self): # queryparams
		dev = self.unpacker.unpack_int()
		self.turn_around()
##		print 'queryparams:', dev
		params = al.queryparams(dev)
##		print 'queryparams ->', params
		self.packer.pack_params(params)
	def handle_2(self): # getparams
		dev, params = self.unpacker.unpack_int_params()
		self.turn_around()
##		print 'getparams:', dev, params
		al.getparams(dev, params)
##		print 'getparams ->', params
		self.packer.pack_params(params)
	def handle_3(self): # setparams
		dev, params = self.unpacker.unpack_int_params()
		self.turn_around()
##		print 'setparams:', dev, params
		al.setparams(dev, params)
	def handle_4(self): # getname
		dev, descr = self.unpacker.unpack_int_int()
		self.turn_around()
##		print 'getname:', dev, descr
		self.packer.pack_string(al.getname(dev, descr))
	def handle_5(self): # getdefault
		dev, descr = self.unpacker.unpack_int_int()
		self.turn_around()
##		print 'getdefault:', dev, descr
		self.packer.pack_int(al.getdefault(dev, descr))
	def handle_6(self): # getminmax
		dev, descr = self.unpacker.unpack_int_int()
		self.turn_around()
##		print 'getminmax:', dev, descr
		self.packer.pack_int_int(al.getminmax(dev, descr))

	def handle_11(self): # openport
		name, mode, config_flat = self.unpacker.unpack_openport()
		self.turn_around()
##		print 'openport:', name, mode, config_flat
		queuesize, width, channels, sampfmt, floatmax = config_flat
		try:
			c = al.newconfig()
			c.setqueuesize(queuesize)
			c.setwidth(width)
			c.setchannels(channels)
			c.setsampfmt(sampfmt)
			c.setfloatmax(floatmax)
			p = al.openport(name, mode, c)
		except RuntimeError:
			self.packer.pack_int(-1) # Should get error code?
			return
		for i in range(len(self.all_ports)):
			if self.all_ports[i] is None:
				self.all_ports[i] = p
				break
		else:
			i = len(self.all_ports)
			self.all_ports.append(p)
##		print 'openport ->', i
		self.packer.pack_int(i)
	def handle_12(self): # closeport
		i = self.unpacker.unpack_int()
		self.turn_around()
##		print 'closeport:', i
		p = self.getport(i)
		if p is None:
			return
		p.closeport()
		self.all_ports[i] = None
	def handle_13(self): # getfilled
		i = self.unpacker.unpack_int()
		self.turn_around()
##		print 'getfilled:', i
		p = self.getport(i)
		if p is None:
			return
		self.packer.pack_int(p.getfilled())
	def handle_14(self): # getfillable
		i = self.unpacker.unpack_int()
		self.turn_around()
##		print 'getfillable:', i
		p = self.getport(i)
		if p is None:
			return
		self.packer.pack_int(p.getfillable())
	def handle_15(self): # readsamps
		i, n = self.unpacker.unpack_readsamps()
		self.turn_around()
##		print 'readsamps:', i, n
		p = self.getport(i)
		if p is None:
			return
		buffer = p.readsamps(n)
		self.packer.pack_string(buffer)
	def handle_16(self): # writesamps
		i, buffer = self.unpacker.unpack_writesamps()
		self.turn_around()
##		print 'writesamps:', i, len(buffer)
		p = self.getport(i)
		if p is None:
			return
		p.writesamps(buffer)
	def handle_17(self): # getfillpoint
		i = self.unpacker.unpack_int()
		self.turn_around()
##		print 'getfillpoint:', i
		p = self.getport(i)
		if p is None:
			return
		self.packer.pack_int(p.getfillpoint())
	def handle_18(self): # setfillpoint
		i = self.unpacker.unpack_int()
		fillpoint = self.unpacker.unpack_int()
		self.turn_around()
##		print 'setfillpoint:', i, fillpoint
		p = self.getport(i)
		if p is None:
			return
		p.setfillpoint(fillpoint)
	def handle_19(self): # getconfig
		i = self.unpacker.unpack_int()
		self.turn_around()
##		print 'getconfig:', i
		p = self.getport(i)
		if p is None:
			return
		c = p.getconfig()
		config_flat = c.getqueuesize(), c.getwidth(), \
			      c.getchannels(), c.getsampfmt(), c.getfloatmax()
		self.packer.pack_config(config_flat)
	def handle_20(self): # setconfig
		i = self.unpacker.unpack_int()
		config_flat = self.unpacker.unpack_config()
		self.turn_around()
##		print 'setconfig:', i, config_flat
		p = self.getport(i)
		if p is None:
			return
		queuesize, width, channels, sampfmt, floatmax = config_flat
		c = al.newconfig()
		# (You can't change queuesize and channels of an open port)
		# c.setqueuesize(queuesize)
		c.setwidth(width)
		# c.setchannels(channels)
		c.setsampfmt(sampfmt)
		c.setfloatmax(floatmax)
		p.setconfig(c)
	def handle_21(self): # getstatus
		i = self.unpacker.unpack_int()
		params = self.unpacker.unpack_params()
		self.turn_around()
##		print 'getstatus:', i, params
		p = self.getport(i)
		if p is None:
			return
		p.getstatus(params)
		self.packer.pack_params(params)


def main():
	s = DALServer()
	s.register()
	print 'DAL server starting...'
	try:
		try:
			s.forkingloop()
		except KeyboardInterrupt:
			print 'DAL server interrupted.'
	finally:
		s.unregister()


main()
