# Print statistics after wwwhunt.py has run

import dbm
import string
import sys
import wwwlib
import regex

done = dbm.open('@done', 'r', 0)

addrlist = done.keys()
print 'Found', len(addrlist), 'documents'

byhost = {}
for addr in addrlist:
	scheme, host, port, path, search, anchor = \
		wwwlib.parse_addr(addr)
	if not byhost.has_key(host):
		byhost[host] = []
	byhost[host].append(addr)
print 'Found', len(byhost), 'hosts'

hosts = byhost.keys()
for i in range(len(hosts)):
	parts = string.splitfields(hosts[i], '.')
	parts.reverse()
	hosts[i] = parts
hosts.sort()

for i in range(len(hosts)):
	parts = hosts[i]
	parts.reverse()
	host = string.joinfields(parts, '.')
	hosts[i] = host

for host in hosts:
	addrs = byhost[host]
	print host, len(addrs),
##	if len(addrs) > 2:
##		print 'e.g.', addrs[0], addrs[-1],
##	else:
##		for a in addrs: print a,
	print

for host in hosts:
	print
	print '---', host, '---'
	good = 0
	for a in byhost[host]:
		title = done[a]
		if regex.match('^([0-9]+, ', title) > 0:
			print 'Error:', a, title
		else:
			good = good + 1
	print 'Has', good, 'good entries'

while 1:
	key = raw_input('Enter host or addr: ')
	if byhost.has_key(key):
		print byhost[key]
	elif done.has_key(key):
		print done[key]
	else:
		print 'Huh?'
