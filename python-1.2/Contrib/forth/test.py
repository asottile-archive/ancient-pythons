#!/usr/Util/bin/python
# ----------------------------------------------------------	
# Test driver.  Add to this as functionality is augmented.
# ----------------------------------------------------------	

import py4th

def test ():    
    already_tested = 0
    print '***** Testing simple postfix program'
    f = py4th.InnerInterpreter()
    if already_tested:

    # Compile and run a simple program.

	s = '2 3 + . 3 4 ^ .'
	t = f.p_compile (s)
	print s, '->', t
	f.p_interp (t)

    ## This section predated the implementation of ':-;' and is no longer
    ## needed.
    ## ------------------------------
    ##    # Now add program as a new word to the dictionary, then invoke it.
    ##
    ##    f.__stack.push(t)
    ##    f.__stack.push('junk')
    ##    f.p_def()
    ##    f.p_interp (['junk'])

	# Test assignment (!) word.

	print '***** Testing VARIABLE ! and @'
	s = '19 variable a 3 a @ * . cr'
	t = f.p_compile(s)
	print s, '->', t
	f.p_interp(t)

	try:
	    s = 'b @ . cr'
	    t = f.p_compile(s)
	    f.p_interp(t)
	except InnerInterpreterError, x:
	    print 'This should fail'

	# Test dup and swap

	print '***** Testing dup and swap'
	s = '20 dup  . cr . cr'
	t = f.p_compile(s)
	print s, '->', t
	print 'should see 20\\n20\\n'
	f.p_interp(t)

	s = '5 10 swap . cr . cr'
	t = f.p_compile(s)
	print s, '->', t
	print 'should see \\n5\\n10\\n'
	f.p_interp(t)

	# Test : , ;, and forget

	print '***** Testing colon definitions and FORGET'
	s = ': sq dup * ; 2 sq 3 sq 100 sq . cr . cr . cr'
	t = f.p_compile(s)
	print s, '->', t
	print 'Should see 10000\\n9\\n4\\n'
	f.p_interp(t)

	print 'forgetting sq'
	f.p_interp(f.p_compile('4 variable d 5 variable e'))
	f.p_interp(f.p_compile('d @ e @ . cr . cr'))
	f.p_interp(f.p_compile('forget sq'))
	try:
	    print f.__vocabulary['sq'] # It better not find this.
	except KeyError, k:
	    print 'sq forgotten' # Exception is ok.

	try:
	    print f.__vars['d'] # It better not find this.
	except KeyError, k:
	    pass # Exception is ok.

	try:
	    print f.__vars['e'] # It better not find this.
	except KeyError, k:
	    print 'FORGET works' # Exception is ok.

	# Everything defined since sq is also forgotten - good!

# Test code for prepass.

    s1 = ': nestor 10 0 do if 1  . cr'
    s2 = 'else dup 2 * then . . cr +loop ;'
    t1 = f.p_compile (s1)
    t2 = f.p_compile (s2)
    tf = t1[0:]
    tf = t1 + t2
    print 'tf =', tf

    print 't1 =', t1
    print 't2 =', t2
    u1 = f.c_prepass (tf)
    print 'u1 =', u1


##    f.p_interp(u)

##    print f.__vocabulary

##    f.p_interp(f.c_prepass(f.p_compile('nestor')))

### Run the test program when called as a script
##
##if __name__ == '__main__':
##    test()

test ()
