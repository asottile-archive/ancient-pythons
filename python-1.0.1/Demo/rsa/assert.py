

error = 'assert.error'

def assert(value):
	if value:
		return
	raise error, 'Assertion failed'

def fatal(msg):
	print 'FATAL:', msg
	assert(0)
