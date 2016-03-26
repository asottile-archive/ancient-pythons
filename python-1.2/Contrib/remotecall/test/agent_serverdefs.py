"""Definitions for the RemoteCall demo server.

Didn't have time to do anything useful, so this demo
is really dumb.
"""

class StupidServer:
	def __init__(self):
		self._a_ = 1
		self._b_ = range(10)

	def increase_a(self):
		self._a_ = self._a_ + 1

	def set_b_ix(self, ix, value):
		self._b_[ix] = value

def new_server():
	return StupidServer()

