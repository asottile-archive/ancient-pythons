"""Definitions common for both clients and servers"""

# Mode to execute request in on server side
EXEC   = 0
EVAL   = 1
CALL   = 2
SETATTR= 3

def picklify(objs):
	from StringIO import StringIO
	from pickle import Pickler
	sio = StringIO()
	pickler = Pickler(sio)
	pickler.dump(objs)
	return sio.getvalue()

def unpicklify(pickled_objs):
	from StringIO import StringIO
	from pickle import Unpickler
	sio = StringIO(pickled_objs)
	unp = Unpickler(sio)
	return unp.load()
