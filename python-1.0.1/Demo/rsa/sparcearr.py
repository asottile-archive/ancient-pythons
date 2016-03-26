
from merge import gluerange

class SparceArr:

	def __init__(self, keys, items):
		#print 'SparceArr.__init__' + `self, keys, items`
		for i in range(len(keys)):
			if keys[i] in keys[:i]:
				raise ValueError, 'sparcearr: double keys'
		self._init(keys, items)

	def _init(self, keys, items):
		self._keys = keys
		self._items = items

	def keys(self):
		return self._keys

	def has_key(self, key):
		return (key in self.keys())

	def _one_tuple(self, index):
		return ((self._keys[index], self._items[index]),)

	def _the_tuples(self):
		if len(self):
			return gluerange(0, len(self), self._one_tuple)
		else:
			return ()

	def __repr__(self):
		the_tuples = self._the_tuples()
		if len(self) == 1:
			argstr = '(' + `the_tuples[0]` + ')'
		else:
			argstr = `the_tuples`
		#argstr = `self._keys, self._items`
		return 'sparcearr' + argstr
		
	def __len__(self):
		#print 'SparceArr.__len__(' + `self` + ')'
		return len(self._keys)

	def __cmp__(self, other):
		if type(other) != type(self):
			other = sparcearr(other)
		st, ot = self._the_tuples(), other._the_tuples()
		if ot < st:
			return 1
		elif ot > st:
			return -1
		else:
			return 0

	def __getitem__(self, key):
		#print 'SparceArr.__getitem__' + `self, key`
		try:
			return self._items[self._keys.index(key)]
		except ValueError:
			raise KeyError, key
		

	def __setitem__(self, key, value):
		#print 'SparceArr.__setitem__' + `self, key, value`
		if key in self._keys:
			self._items[self._keys.index(key)] = value
		else:
			self._keys.append(key)
			self._items.append(value)

	def __delitem__(self, key):
		#print 'SparceArr.__delitem__' + `self, key`
		ix = self._keys.index(key)
		del self._keys[ix], self._items[ix]

	def __add__(self, other):
		if type(other) != type(self):
			other = sparcearr(other)
		for i in other.keys():
			if i in self._keys:
				return ValueError, \
					  'sparcearr: can\'t add two arrays with same keys'
		return SparceArr(self._keys + other._keys, \
			  self._items + other._items)

		
def sparcearr(*arg):
	if len(arg) == 0:
		return SparceArr([], [])
	if len(arg) == 1 and type(arg[0]) == type([]):
		return SparceArr(range(len(arg[0])), arg[0][:])
	if len(arg) == 2 \
		  and type(arg[0]) == type([]) \
		  and type(arg[1]) == type([]) \
		  and len(arg[0]) == len(arg[1]):
		return SparceArr(arg[0][:], arg[1][:])
	if len(arg) > 0 and type(arg[0]) == type(()) and len(arg[0]) == 2:
		keys, items = [], []
		for i in arg:
			if type(i) != type(()) or len(i) != 2:
				break
			keys.append(i[0])
			items.append(i[1])
		else:
			return SparceArr(keys, items)
	raise TypeError, 'sparcearr(): invalid types of args, number of args or length of args'

