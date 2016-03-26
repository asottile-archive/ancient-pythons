#!/usr/local/bin/python

# An example script that implements a pop3 client mail message
# retrieval and delivery system

import os
from pop3 import *
from smtp import *
from StringIO import *
from rfc822 import *

users = {'yourusernamehere' : 'yourpasswordhere'}

lock_file = '/usr/spool/mqueue/pop.lock'

# assign log handler

def main():
    if (not os.path.exists(lock_file)):
	lck = open(lock_file, 'w', 0)

	for user in users.keys():
	    get_mail(user, users[user])

	lck.close()

	os.system("rm " + lock_file)
    else:
	sys.stderr.write("POP lock file exists\n")

    sys.exit(0)

def get_mail(user, passwd):
    pop = POP3(2)
    smtp = SMTP(2)
    msgs = []

    pop.open_server(sys.argv[1])

    smtp.open_server(gethostname())
    smtp.hello(gethostname())

    try:
	pop.login(user, passwd)
    except "POP3Error", errmsg:
	err_handler("Error logging to POP server: %s" % errmsg, pop, smtp)

    msgdict = pop.list()

    for msgnum in msgdict.keys():
	try:
	    msg = pop.retrieve(msgnum)
	except "POP3Error", errmsg:
	    err_handler("error retrieving message %d" % msgnum, 
			pop, smtp)
	    
	f = StringIO(string.joinfields(msg, ''))
	m = Message(f)
	(addr, name) = m.getaddr('From')

	try:
	    smtp.mail_from('<' + addr + '>')
	except:
	    err_handler("error sending message, returning it to host", 
			pop, smtp)

	try:
	    smtp.mail_to(user)
	except:
	    err_handler("error sending message, returning it to host", 
			pop, smtp)

	try:
	    smtp.data(msg)
	except:
	    err_handler("error sending message, returning it to host", 
			pop, smtp)

	f.close()

	try:
	    pop.delete(msgnum)
	except:
	    err_handler("error deleting message %d" % msgnum, 
			pop, smtp)

    pop.close()
    smtp.close()

def err_handler(errmsg, pop, smtp):
    sys.stderr.write(sys.argv[1] + ": " + errmsg)
    pop.reset()
    pop.close()
    smtp.close()
    os.system("rm " + lock_file)
    sys.exit(4)

try:
    main()
except KeyboardInterrupt:
    pass
