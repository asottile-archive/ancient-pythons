##Subject: simple finite state machine class
##From: skip@dolphin.automatrix.com (Skip Montanaro)
##To: python-list@cwi.nl
##Date: 21 Mar 1995 03:12:00 GMT
##X-Newsgroups: comp.lang.python
##X-Organization: Automatrix, Inc.
##
##
##I got tired of an ever increasing if/elif/elif/elif/.../else statement used
##to implement a finite state machine today and broke down and wrote a simple
##one (after poking around the 1.1.1 distribution and not seeing anything).
##It's pretty simple to use.  For example, I have a gutless keyword-based
##command language (sort of like tcl :-) used to implement an interface to
##Musi-Cal our concert calendar.  You send mail messages that look like
##
##	get
##	type folk
##	city New York
##	date 1 April 1995 - 30 June 1995
##	end
##
##or
##
##	add
##	performer Indigo Girls
##	type folk,rock
##	venue Bottom Line
##	city New York
##	state NY
##	date 12 April 1992
##	end
##
##and it returns a list of entries from the database satisfying the
##constraints or adds a new entry to the database.  After a few commands and
##subcommands were added to the inline fsm it got quite unwieldy.  After
##writing the fsm class I now have:
##
##    from fsm import FSM, FSMError
##
##    fsm = FSM()
##    #       state    input  next      action
##    #                       state 
##    fsm.add('start', 'add', 'adding', start_add)
##    fsm.add('start', 'get', 'getting', start_get)
##    fsm.add('start', 'help', 'done', do_help)
##    fsm.add('start', 'clear', 'start', do_clear)
##    fsm.add('start', 'default', 'defaulting', start_default)
##    fsm.add('start', None, 'start', noop)
##    fsm.add('start', EOF, 'done', noop)
##
##    ...
##
##    fsm.start('start')
##
##    ...
##
##    try:
##	for rawline in lines:
##	    ...
##	    word = ...
##	    ...
##	    fsm.execute(word)
##	fsm.execute(EOF)
##	...
##    except FSMError:
##	send_help(user, email, reply)
##
##The code is no shorter since all the little bits of inline code turned into
##a bunch of little functions, but it's a heck of a lot easier to understand
##the structure looking at a set of fsm.add() calls.
##
##(Side note:  I remember writing a finite state machine class in C for LYMB.
##It wasn't this easy... :-)
##
##Here's the FSM class:

# finite state machine class

# class stores dictionary of state/input keys, values are
# next state and action

# when searching for matching state/input key, exact match
# is checked first, then state/None as default for that state.

# action is a function to execute which takes the current state
# and input as arguments

FSMError = 'Invalid input to finite state machine'

class FSM:
    def __init__(self):
	self.states = {}
	self.state = None
	self.dbg = None

    # add another state to the fsm
    def add(self, state, input, newstate, action):
	self.states[(state, input)] = (newstate, action)

    # perform a state transition and action execution
    def execute(self, input):

	si = (self.state, input)
	sn = (self.state, None)
	# exact state match?
	if self.states.has_key(si):
	    newstate, action = self.states[si]
	# no, how about a None (catch-all) match?
	elif self.states.has_key(sn):
	    newstate, action = self.states[sn]

	if self.dbg != None:
	    self.dbg.write('State: %s / Input: %s / Next State: %s / Action: %s\n' % \
			   (self.state, input, newstate, action))

	apply(action, (self.state, input))
	self.state = newstate

    # define the start state
    def start(self, state):
	self.state = state

    # assign a writable file to catch debugging transitions
    def debug(self, out):
	self.dbg = out



##Skip Montanaro	skip@automatrix.com			(518)372-5583
##Musi-Cal: http://www.calendar.com/concerts/ -or- concerts@calendar.com
##Internet Conference Calendar: http://www.calendar.com/conferences/
