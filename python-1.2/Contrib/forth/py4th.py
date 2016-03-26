#!/usr/Util/bin/python
#
# @(#)py4th.py	1.2  94/12/07
#
# Forth in Python (py4th).
#
##    This module implements a postfix interpreter class that
##    can be instantiated as the inner interpreter or as a forth-ish
##    interactive interpreter.  The inner interpreter has two methods
##    called p_compile and p_interp that are the core methods.  Compile
##    takes a string argument and returns a list that is executable by
##    the p_interp method.
##
##    As of this version (12/6/94) there are a few important features
##    that need to be added, namely if-else-then and do-loop structures.
##    Doing so may require that the "for" construct used in p_interp
##    be replaced by a while loop that iterates over the program with
##    a program counter instead of the nice, clean, pc-less way it's done
##    now.  I had thought about implementing these as follows:
##
##	for IF-ELSE-THEN:
##
##	    given -- IF wordlist1 ELSE wordlist2 THEN
##	    wordlist1 and wordlist2 would be compiled as embedded
##	    lists within the current list.  For example:
##
##		a @ if dup * else dup dup * * then
##
##	    would compile into
##
##		['a', '@', 'if', ['dup', '*'], 'else', [ 'dup', 'dup',
##			 '*', '*']]
##
##	    so that p_interp could then treat the wordlists as single
##	    words and pass then to recursive invocations of itself.
##
##	    I have a similar scheme in mind for DO-LOOPs.
##
##		10 0 do i . cr loop 
##
##	    would become 
##
##		['10', '0', 'do', ['i', '.', 'cr', 'loop']]
##
##	    One way to do it might be to have a prepass before
##	    p_interp and after p_compile.  Since these control structures
##	    are only allowed inside definitions, perhaps p_semicolon
##	    could be where this happens.  It could then build the
##	    sublists and add the code required for loop increments
##	    and proper skipping (else over if)  and handling of omitted
##	    parts (if without else or then).
##
##	    Loops use the variable name 'I' for the reference count.
##	    The prepass mentioned above would generate code to store
##	    the current value of 'I' (if any) as some internally known
##	    variable (e.g., '__I__2371') and restore it once the loop
##	    was finished.
##
##    I have already put the skeleton code in for doing this.  It's a
##    bit of a hack at this point but you can get the gist of what I have
##    in mind from in.
##
##    Author: Nick Seidenman
##            SAIC
##            nick@osg.saic.com

import string
import math
import sys
from stack import *

ExitNonError = 'ExitNonError'
InnerInterpreterError = 'InnerInterpreterError'


# InnerInterpreter takes a postfix expression in the form of
#  a python list object and 'executes it'.  It has it's own
#  dictionary, which is initialized with the py4thon primatives and a few

# Operational modes.
Execution = 'Execution'
Definition = 'Definition'
Forgetting = 'Forgetting'
Comment = 'Comment'
Variable = 'Variable'

RunningLevel = 2

class InnerInterpreter:
    
    def __init__(self):
	# Create a new stack and dictionary for this interpreter instance.
	self.__stack = Stack()
	self.__rstack = Stack()
	self.__vocabulary = {}
	self.__ulist = []
	self.__vars = {}
	self.__vlist = []
	self.__mode = Execution
	self.__lastmode = Execution
	self.__runlevel = 0

	# Initialize the new dictionary with words for the primitive
	#  functions.
	self.__vocabulary['.'] = self.p_dot
	self.__vocabulary['cr'] = self.p_cr
	self.__vocabulary['+'] = self.p_plus
	self.__vocabulary['-'] = self.p_minus
	self.__vocabulary['*'] = self.p_multiply
	self.__vocabulary['/'] = self.p_divide
	self.__vocabulary['uminus'] = self.p_uminus
	self.__vocabulary['^'] = self.p_exponent
	self.__vocabulary['variable'] = self.p_variable
	self.__vocabulary['!'] = self.p_assign
	self.__vocabulary['@'] = self.p_dereference
	self.__vocabulary['dup'] = self.p_dup
	self.__vocabulary['swap'] = self.p_swap
	self.__vocabulary['bye'] = self.p_bye
	self.__vocabulary['forget'] = self.p_forget
	self.__vocabulary[':'] = self.p_colon
	self.__vocabulary[';'] = self.p_semicolon
	self.__vocabulary['('] = self.p_lparen
	self.__vocabulary[')'] = self.p_rparen
	self.__vocabulary['vlist'] = self.p_vlist

	# Initialize dictionary with control structures.

	self.__vocabulary['if'] = self.c_if
	self.__vocabulary['else'] = self.c_else
	self.__vocabulary['then'] = self.c_then
	self.__vocabulary['do'] = self.c_do
	self.__vocabulary['loop'] = self.c_loop
	self.__vocabulary['+loop'] = self.c_plusloop

	# Initialize the control structures prepass table.

	self.__ctl_struct = {}
	self.__ctl_struct['do'] = self.c_pp_do
	self.__ctl_struct['loop'] = self.c_pp_loop
	self.__ctl_struct['+loop'] = self.c_pp_plusloop
	self.__ctl_struct['if'] = self.c_pp_if
	self.__ctl_struct['else'] = self.c_pp_else
	self.__ctl_struct['then'] = self.c_pp_then
	

    # Primitive functions (all begin with 'p_'.  Primitive
    #  is defined as a function that must directly manipulate
    #  the interpreter stack.  Defined functions do not do this.

    def p_dot(self):
	result = self.__stack.pop()
	sys.stdout.write (result + ' ')

    def p_cr (self):
	print

    def p_plus(self):
	y = string.atof(self.__stack.pop())
	x = string.atof(self.__stack.pop())
	self.__stack.push (`y + x`)
	
    def p_minus (self):
	y = string.atof(self.__stack.pop())
	x = string.atof(self.__stack.pop())
	self.__stack.push(`y - x`)

    def p_multiply (self):
	y= string.atof(self.__stack.pop())
	x = string.atof(self.__stack.pop())
	self.__stack.push(`y * x`)

    def p_divide (self):
	y = string.atof(self.__stack.pop())
	x = string.atof(self.__stack.pop())
	self.__stack.push( `b / a`)

    def p_exponent (self):
	y = string.atof(self.__stack.pop())
	x = string.atof(self.__stack.pop())
	self.__stack.push( `math.pow(x, y)`)

    def p_uminus (self):
	x = string.atof(self.__stack.pop())
	self.__stack.push (`- x`)

    def p_assign (self):
	word = self.__stack.pop()
	value = self.__stack.pop()
	if self.__vars.has_key (word):
	    self.__vars[word] = value
	else:
	    raise InnerInterpreterError, word

    def p_dereference (self):
	word = self.__stack.pop()
	try:
	    self.__stack.push(self.__vars[word])
	except KeyError, x:
	    raise InnerInterpreterError, word

    def p_dup(self):
	val = self.__stack.pop()
	self.__stack.push(val)
	self.__stack.push(val)

    def p_swap(self):
	a = self.__stack.pop()
	b = self.__stack.pop()
	self.__stack.push(a)
	self.__stack.push(b)
    
    def p_def (self):
	word = self.__stack.pop()
	prog = self.__stack.pop()
##	print 'defining', word, 'as', prog
	self.__vocabulary[word] = prog
	self.__ulist.append(word)

    def p_colon (self):
	if self.__mode == Execution:
	    self.__mode = Definition
	    self.__colon = []
	else:
	    raise InnerInterpreterError, 'nested colon'

    def p_semicolon (self):
	if self.__mode == Definition:
	    # Perhaps put prepass in here to scan for
	    #  IF-ELSE-THEN and DO-LOOP and create sublists
	    #  from these?
	    prog = self.__colon[1:]
	    self.__stack.push(prog)
	    self.__stack.push(self.__colon[0])
	    del self.__colon
	    self.p_def()
	    self.__mode = Execution
	else:
	    raise InnerInterpreterError, 'nested semicolon'

    def p_forget (self):
	self.__mode = Forgetting

    def p_bye (self):
	raise ExitNonError

    def p_compile (self, text):
	return string.split(text)

    def p_lparen (self):
	if self.__mode != Comment:
	    self.__lastmode = self.__mode
	    self.__mode = Comment
	    
    def p_rparen (self):
	if self.__mode == Comment:
	    self.__mode = self.__lastmode
	else:
	    raise InnerInterpreterError, ')'

    def do_forget (self, word):
	if self.__vocabulary.has_key(word) or self.__vars.has_key(word):
	    i = self.__ulist.index(word) ## Should be in here.
	    ul = len(self.__ulist)
	    for j in range (i, ul):
		if self.__vocabulary.has_key(self.__ulist[i]):
		    del self.__vocabulary[self.__ulist[i]]
		elif self.__vars.has_key(self.__ulist[i]):
		    del self.__vars[self.__ulist[i]]
		else:
		    raise InnerInterpreterError, 'system error'
		del self.__ulist[i]
	else:
	    raise InnerInterpreterError, 'system error'

	self.__mode = Execution

    def p_variable (self):
	self.__lastmode = self.__mode
	self.__mode = Variable

    def do_variable (self, varName):
	self.__vars[varName] = self.__stack.pop()
	self.__ulist.append(varName)
	self.__mode = self.__lastmode

    def p_vlist (self):
	vlist = self.__vocabulary.keys()
	vlist.sort()
	for k in vlist: 
	    sys.stdout.write (k + ' ')
	
    ###
    ### Control structures (if then else, do loop, etc).
    ###

    def c_if (self):
	if self.__runlevel < RunningLevel:
	    raise InnerInterpreterError, 'if'

    def c_else (self):
	if self.__runlevel < RunningLevel:
	    raise InnerInterpreterError, 'else'

    def c_then (self):
	if self.__runlevel < RunningLevel:
	    raise InnerInterpreterError, 'then'

    def c_do (self):
	if self.__runlevel < RunningLevel:
	    raise InnerInterpreterError, 'do'

    def c_pp_do (self, scan):
	self.__rstack.push(scan[0:])
	scan = []
	scan.append ('do')
	self.__rstack.push(scan[0:])
	scan = []
	return scan

    def c_pp_if (self, scan):
	self.__rstack.push(scan[0:])
	scan = []
	scan.append ('if')
	self.__rstack.push(scan[0:])
	scan = []
	return scan

    def c_loop (self):
	if self.__runlevel < RunningLevel:
	    raise InnerInterpreterError, 'loop'

    def c_pp_loop (self, scan):
	try:
	    result = self.__rstack.pop()
	except StackError, x:
	    raise InnerInterpreterError, \
		  'illegal control structure: ' + '\"loop\" without \"do"'

	if result[0] == 'do':
	    result.append(scan)
	    result2 = self.__rstack.pop()
	    result2.append(result[0:])
	    return result2

	else:
	    raise InnerInterpreterError, \
		  'illegal control structure: ' + '\"loop\" without \"do\"'

    def c_pp_plusloop (self, scan):
	try:
	    result = self.__rstack.pop()
	except StackError, x:
	    raise InnerInterpreterError, \
		  'illegal control structure: ' + '\"+loop\" without \"do"'

	if result[0] == 'do':
	    scan.append('+loop')
	    result.append(scan)
	    result2 = self.__rstack.pop()
	    result2.append(result[0:])
	    return result2

	else:
	    raise InnerInterpreterError, \
		  'illegal control structure: ' + '\"+loop\" without \"do\"'

    def c_pp_else (self, scan):
	try:
	    result = self.__rstack.pop()
	except StackError, x:
	    raise InnerInterpreterError, 'illegal control structure'

	if result[0] != 'if':  # ERROR
	    raise InnerInterpreterError, 'illegal control structure'
	result.append(scan[0:])
	self.__rstack.push(result[0:])
	scan = []
	return scan

    def c_pp_then (self, scan):
	try:
	    result = self.__rstack.pop()
	except StackError, x:
	    raise InnerInterpreterError, 'illegal control structure'

	if result[0] == 'if':
	    result.append(scan)
	    result2 = self.__rstack.pop()
	    result2.append(result[0:])
	    return result2

	else:
	    raise InnerInterpreterError, 'illegal control structure'


    def c_plusloop (self):
	if self.__runlevel < RunningLevel:
	    raise InnerInterpreterError, '+loop'

    def c_prepass (self, prog):
	self.__rstack.flush()
	scan = []
	for word in prog:
	    if self.__ctl_struct.has_key(word):
		scan = self.__ctl_struct[word](scan)
	    else:
		scan.append(word)

	return scan

# This is the inner interpreter itself.  It will execute the
#  code body passed in the form of a python list as 'prog'.
    def p_interp (self, prog):
	for word in prog:
	    # Are we in comment mode?
	    if self.__mode == Comment:
		if word == ')':
		    self.p_rparen()
		continue

	    # Are we in execution mode or definition mode?
	    elif self.__mode == Definition:
		if word == ';':
		    self.p_semicolon()
		else:
		    self.__colon.append(word)
		continue

	    elif self.__mode == Variable:
		self.do_variable (word)
		continue

	    # See if this is a word we are supposed to forget.
	    elif self.__mode == Forgetting:
		self.do_forget (word)
		continue

	    # If it isn't in the dictionary to begin with, then it must
	    #  be a constant: push it on the stack
	    if type(word) != type([]) and not self.__vocabulary.has_key(word):
		self.__stack.push(word)
		continue
	    
	    # It is in the dictionary, but it may be a defined word
	    #  rather than a primitive.  Chase it down to either a
	    #  primitive, a constant, or another code body.  In the
	    #  latter case, recurse with the new code body.
	    else:
		current_word = word
		try:
		    while self.__vocabulary.has_key (self.__vocabulary[current_word]):
			current_word = self.__vocabulary[current_word]
		except TypeError, x:
		    pass  # Ok, since this is probably because the
		          # it's a list, or a primative.

		# If what we have is another program (non-primative word)
		#  then we run interp recursively to execute the word's text.
		if type(current_word) == type([]):
		    self.__runlevel = self.__runlevel + 1
		    self.p_interp(current_word)
		    self.__runlevel = self.__runlevel - 1

		elif type(self.__vocabulary[current_word]) == type([]):
		    self.__runlevel = self.__runlevel + 1
		    self.p_interp(self.__vocabulary[current_word])
		    self.__runlevel = self.__runlevel - 1

		elif type(self.__vocabulary[current_word]) == type (self.p_def):
		    self.__vocabulary[current_word]()

		# Whatever it is at this point just gets pushed onto
		#  the stack.  It should be some sort of constant.
		else:
		    self.__stack.push(self.__vocabulary[current_word])

# Simple outter interpreter for Py4th.  I envision this as being
# augmented with thread support to allow multiple instances of
# the interpreter to provide a multitasking "forth" environment.

class Py4th:
    def __init__(self, input=sys.stdin):
	self.input = input
	self.interpreter = InnerInterpreter ()

    def go (self):
	try:
	    while 1:
		try:
		    input = self.input.readline ()
		    code = self.interpreter.p_compile (input)
		    self.interpreter.p_interp (code)
		    if self.input.isatty () and self.interpreter.__mode == Execution:
			print 'OK'
		except (InnerInterpreterError, StackError), err_str:
		    if err_str != 'stack underflow':
			print err_str, '?'
		    else:
			print err_str
		    self.interpreter.__stack.flush()

	except ExitNonError:
	    if self.input.isatty ():
		print 'goodbye'
	    pass


##if __name__ == '__main__':
##    print 'Py4th -- forth in python'
##    p = Py4th()
##    p.go()
##    sys.exit(0)	
