# Utilities shared by www.py and wwww.py

import os
import wwwlib
import marshal


# Determine the absolute address of system and user home
system_home = wwwlib.WWW_HOME
system_home = wwwlib.full_addr('file:', system_home)
user_home = system_home
if os.environ.has_key('WWW_HOME'):
	user_home = os.environ['WWW_HOME']
	user_home = wwwlib.full_addr('file:', user_home)


# Load some object from a file
def load_file(user_name, default_name):
	name = user_name
	if not name:
		name = default_name
		if os.environ.has_key('HOME'):
			name = os.path.join(os.environ['HOME'], name)
	#
	try:
		f = open(name, 'r')
		contents = marshal.load(f)
		f.close()
		return contents
	except IOError, msg:
		if user_name:
			print user_name, ':', msg
		return None


# Save some object on a file
def save_file(contents, user_name, default_name):
	name = user_name
	if not name:
		name = default_name
		if os.environ.has_key('HOME'):
			name = os.path.join(os.environ['HOME'], name)
	#
	if os.path.exists(name):
		try:
			os.unlink(name + '~')
		except os.error:
			pass
		try:
			os.rename(name, name + '~')
		except os.error, msg:
			print 'Failed to back-up', `name`, ':', msg
	try:
		f = open(name, 'w')
		marshal.dump(contents, f)
		f.close()
	except IOError, msg:
		print name, ':', msg
