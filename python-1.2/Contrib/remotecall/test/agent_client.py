from Agent import Agent
import sys

if len(sys.argv) <= 2:
	port = eval(sys.argv[1])
else:
	host = eval(sys.argv[1])
	port = eval(sys.argv[2])

print "Create agent for module serverdefs"
# Here we create an agent for a module!
agent = Agent('serverdefs', '138.221.22.200', port)
print "Ok, agent created and configured"

print "\nThe following methods are available:"

dict = agent.__dict__
for item in dict.keys():
	if hasattr(dict[item], '__class__') and dict[item].__class__ == Agent.Method:
		print ' '*3, item

print "\nCreate an instance of a server object"
server = agent.new_server()

print "\nThe following methods are available:"
dict = server.__dict__
for item in dict.keys():
	if hasattr(dict[item], '__class__') and dict[item].__class__ == Agent.Method:
		print ' '*3, item


def print_attrs(server):
	print "Values of attributes:"
	print "  _a_ =", server._a_
	print "  _b_ =", server._b_

print
print_attrs(server)

print "\nCall server.increase_a()"
server.increase_a()
print_attrs(server)

print "\nCall server.set_b_ix()"
from Complex import Complex
item = Complex(3.14, 2.71828)
server.set_b_ix(3, item)
print_attrs(server)

# Raise an exception on server side, and catch it
print "\nCatching a remote exception:"
try:
	server.increase_a('This argument is not expected')
except TypeError:
	print 'Oops, I caught an exception: (%s, %s)' % (sys.exc_type, sys.exc_value)
