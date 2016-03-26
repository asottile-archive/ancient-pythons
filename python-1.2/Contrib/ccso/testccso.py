#!/usr/local/bin/python
# -*- Mode: Python -*-

# Copyright 1994 by Jeffrey C. Ollie -- All Rights Reserved

import ccso
from ccso import CCSO

c = CCSO('ns.uiowa.edu')
print c.query('jeff ollie')
try:
	print c.query('smith')
except ccso.error, x:
	print x
try:
	c.query('gomer')
except ccso.error, x:
	print x
try:
	print c.othercmd('siteinfo')
except ccso.error, x:
	print x
try:
	print c.login('jeffrey-ollie','xxxxxxx')
	print c.alias
	print c.logout()
except ccso.error, x:
	print x
try:
	print c.login('bogus-name','bogus-passwd')
except ccso.error, x:
	print x
try:
	print c.get_email('weeg')
except ccso.error, x:
	print x
#c.close()
