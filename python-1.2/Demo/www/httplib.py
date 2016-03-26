# HTTP protocol interface

DEF_PORT = 80
OLD_PORT = 2784

# Get an HTML file from an HTML server, converting (optional) CRLF to LF
def get_htmlfile(host, port, searchaddr):
	text = ''
	f = send_request(host, port, 'GET ' + searchaddr)
	while 1:
		line = f.readline()
		if not line:
			break
		if line[-2:] == '\r\n':
			line = line[:-2] + '\n'
		text = text + line
	f.close()
	return text

# Send a selector to a given host and port, return an open file from
# which the reply can be read
def send_request(host, port, request):
	import socket
	if not port:
		port = DEF_PORT
	elif type(port) == type(''):
		import string
		port = string.atoi(port)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((host, port))
	except socket.error, msg:
		if type(msg) == type(()) and len(msg) == 2 and \
			msg[0] == 127 and port == DEF_PORT:
			# Try the old default port
			s.close()
			return send_request(host, OLD_PORT, request)
		else:
			raise socket.error, msg
	s.send(request + '\r\n')
	s.shutdown(1)
	return s.makefile('r')
