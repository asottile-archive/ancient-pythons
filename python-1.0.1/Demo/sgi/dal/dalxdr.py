# Packer and Unpacker extensions for Distributed Audio Library (DAL)

import rpc

class DALPacker(rpc.Packer):
	def pack_openport(self, arg):
		name, mode, config = arg
		self.pack_string(name)
		self.pack_string(mode)
		self.pack_config(config)
	def pack_setconfig(self, arg):
		i, config = arg
		self.pack_int(i)
		self.pack_config(config)
	def pack_config(self, arg):
		queuesize, width, channels, sampfmt, floatmax = arg
		self.pack_int(queuesize)
		self.pack_int(width)
		self.pack_int(channels)
		self.pack_int(sampfmt)
		self.pack_float(floatmax)
	def pack_readsamps(self, arg):
		i, n = arg
		self.pack_int(i)
		self.pack_int(n)
	def pack_writesamps(self, arg):
		i, buffer = arg
		self.pack_int(i)
		self.pack_string(buffer)
	def pack_int_int(self, arg):
		i1, i2 = arg
		self.pack_int(i1)
		self.pack_int(i2)
	def pack_int_params(self, arg):
		i, params = arg
		self.pack_int(i)
		self.pack_params(params)
	def pack_params(self, params):
		self.pack_list(params, self.pack_int)

class DALUnpacker(rpc.Unpacker):
	def unpack_openport(self):
		name = self.unpack_string()
		mode = self.unpack_string()
		config = self.unpack_config()
		return name, mode, config
	def unpack_setconfig(self):
		i = self.unpack_int()
		config = self.unpack_config()
		return i, config
	def unpack_config(self):
		queuesize = self.unpack_int()
		width = self.unpack_int()
		channels = self.unpack_int()
		sampfmt = self.unpack_int()
		floatmax = self.unpack_float()
		return queuesize, width, channels, sampfmt, floatmax
	def unpack_readsamps(self):
		i = self.unpack_int()
		n = self.unpack_int()
		return i, n
	def unpack_writesamps(self):
		i = self.unpack_int()
		buffer = self.unpack_string()
		return i, buffer
	def unpack_int_int(self):
		i1 = self.unpack_int()
		i2 = self.unpack_int()
		return i1, i2
	def unpack_int_params(self):
		i = self.unpack_int()
		params = self.unpack_params()
		return i, params
	def unpack_params(self):
		return self.unpack_list(self.unpack_int)
