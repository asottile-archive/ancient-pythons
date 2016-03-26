#!/usr/local/bin/python
# -*- Mode: Python -*-

# (C) 1994 by Jeffrey C. Ollie -- All Rights Reserved

# Version 0.2, November 10, 1994
#
# Bugs fixed:
#
# o In method query(), resp[0] and resp[1] needed to be changed to
# response[0] and response[1].  Thanks to Ray Price <rlprice@ka.reg.uci.edu>.
#
# o In get_response(), the return of digits.match() was not checked properly.
#
# Features added:
#
# o login(alias)/logout() methods allow you to log into the database.
# Passwords are currently sent in the clear, but I'm working on adding the
# encrypting of the login challenge.  Unfortunately, this will require some
# C code.
#
# o othercmd(str) method for sending your own commands to the server.  Could
# be useful for sending "make" commands when you are logged in.  Returns
# the raw responses (but parsed out into fields).
#
# o get_email(str) method for looking up e-mail addresses.  Returns a list
# of dictionary objects.  Each dictionary object has two keys: "name" and
# "email".
#
# o The siteinfo attribute is a dictionary object which contains the
# responses parsed out of the "siteinfo" command.
#
# Version 0.1
#
# Original version.

# See the technical report _The CCSO Nameserver Server-Client Protocol_
# by Steve Dorner and Paul Pomes for details about the protocol
# implemented here.  The TR can be found in the CCSO server distribution:
#
#    ftp://vixen.cso.uiuc.edu/pub/qi-2.3.tar.gz
#
# or in the CCSO Nameserver client distribution
#
#    ftp://vixen.cso.uiuc.edu/pub/ph-6.17.tar.gz
#

from socket import socket, getservbyname, AF_INET, SOCK_STREAM
from string import strip, find, atoi
import regex

error = 'CCSO error'

digits = regex.compile('^-?[0-9]+$')

# Read a line from the passed in socket.
# A quick hack, I should work on a better way.

def get_line(sock):
	line = ''
	ch = sock.recv(1)
	while ch != '\n':
		line = line + ch
		ch = sock.recv(1)
	return strip(line)

# Read a line from the socket and parse it into fields.
# There's probably a regex that will do this better, but
# I can't think of it. 

def get_response(sock):
	line = get_line(sock)
	i1 = find(line, ':')
	if i1 == -1:
		raise error, 'response does not match format'
	result_code = atoi(line[:i1])
	i2 = find(line, ':', i1+1)
	if i2 == -1:
		entry_index = None
		field_name = None
		text = strip(line[i1+1:])
	else:
		if digits.match(strip(line[i1+1:i2])) != -1:
			entry_index = atoi(line[i1+1:i2])
			i3 = find(line, ':', i2+1)
			if i3 == -1:
				field_name = None
				text = strip(line[i2+1:])
			else:
				field_name = strip(line[i2+1:i3])
				text = strip(line[i3+1:])
		else:
			entry_index = None
			field_name = strip(line[i1+1:i2])
			text = strip(line[i2+1:])
	return (result_code, entry_index, field_name, text)

class CCSO:
	def __init__(self, host, port='ns'):
		self.alias = None
		self.host = host
		self.siteinfo = {}
		self.port = None
		try:
			if type(port) == type(105):
				self.port = port
			else:
				if digits.match(strip(port)) != -1:
					self.port = atoi(strip(port))
				else:
					self.port = getservbyname(port, 'tcp')
		except:
			if self.port == None:
				self.port = 105
		self.sock = socket(AF_INET, SOCK_STREAM)
		self.sock.connect(self.host, self.port)
		self.sock.send('set verbose=off\r\n')
		response = get_response(self.sock)
		while response[0] < 200:
			response = get_response(self.sock)
		if response[0] != 200:
			raise error, (response[0], response[3])
		self.sock.send('siteinfo\r\n')
		response = get_response(self.sock)
		while response[0] < 200:
			if response[0] == -200:
				self.siteinfo[response[2]] = response[3]
			response = get_response(self.sock)
		if not self.siteinfo.has_key('mailbox'):
			self.siteinfo['mailbox'] = 'email'
	def query(self, str):
		q = 'query ' + strip(str) + ' return all\r\n'
		self.sock.send(q)
		currentindex = None
		currententry = {}
		lastfield = None
		entries = []
		response = get_response(self.sock)
		while response[0] < 200:
			if response[0] == -200:
				if response[1] != currentindex:
					if currentindex != None:
						entries.append(currententry)
					currententry = {}
					currentindex = response[1]
					lastfield = None
				if response[2] == '':
					currententry[lastfield] = currententry[lastfield] + '\n' + response[3]
				else:
					currententry[response[2]] = response[3]
					lastfield = response[2]
			response = get_response(self.sock)
		if response[0] >= 300:
			raise error, (response[0], response[3])
		entries.append(currententry)
		return entries
	def login(self, alias, password):
		q = 'login ' + strip(alias) + '\r\n'
		self.sock.send(q)
		response = get_response(self.sock)
		while response[0] < 200:
			response = get_response(self.sock)
		if response[0] == 200:
			self.alias = alias
			return alias
		elif response[0] == 301:
			self.sock.send('clear '+strip(password)+'\r\n')
			response = get_response(self.sock)
			while response[0] < 200:
				response = get_response(self.sock)
			if response[0] >= 400:
				raise error, (response[0], response[3])
			self.alias = alias
			return alias
		else:
			raise error, (response[0], response[3])
	def logout(self):
		q = 'logout\r\n'
		self.sock.send(q)
		response = get_response(self.sock)
		while response[0] < 200:
			response = get_response(self.sock)
		if response[0] >= 400:
			raise error, (response[0], response[3])
		self.alias = None
	def othercmd(self, str):
		q = strip(str) + '\n\n'
		self.sock.send(q)
		responses = []
		response = get_response(self.sock)
		while response[0] < 200:
			responses.append(response)
			response = get_response(self.sock)
		responses.append(response)
		return responses
# The algorithm for get_email is taken from messages posted to
# the info-ph mailing list by Steve Dorner <sdorner@qualcomm.com>
# and Scott M. Ballew <smb@pern.cc.purdue.edu>.
# Message-ID's: <9411102104.AA14717@pern.cc.purdue.edu>
#               <v03000728aae842fd09b2@[192.17.16.12]>
#               <v0300073baae6af3eb78f@[192.17.16.12]>
	def get_email(self, str):
		mailbox = self.siteinfo['mailbox']
		mailfield = self.siteinfo['mailfield']
		responses = self.query(str)
		addresses = []
		if self.siteinfo.has_key('maildomain') and self.siteinfo['maildomain'] != '':
			maildomain = self.siteinfo['maildomain']
			for entry in responses:
				if entry.has_key(mailbox) and entry[mailbox] != '':
					addresses.append({'name': entry['name'], 'email': entry[mailfield]+'@'+maildomain})
		else:
			for entry in responses:
				if entry.has_key(mailfield) and entry[mailfield] != '':
					addresses.append({'name': entry['name'], 'email': entry[mailfield]})
		return addresses
	def close(self):
		q = 'quit\r\n'
		self.sock.send(q)
		response = get_response(self.sock)
		while response[0] < 200:
			response = get_response(self.sock)
		if response[0] >= 400:
			raise error, (response[0], response[3])
		self.sock.close()
	def __del__(self):
		self.close()
