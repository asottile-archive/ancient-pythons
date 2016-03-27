################################################################################
# Turing machine simulation in Python (to prove that python is Turing
# complete :-))
#
# This program reads in a state transition file (the program) and from
# that and the initial tape that you specify, emulates a Turing machine
# executing that program.  State 0 is the halting state.
#
# Each state transition has the following syntax:
#
#	<state, char> --> <new-state, operation>
#
# Where operation is:
#
#	L	move the tape head left 1 place.
#	R	move the tape head right 1 place.
#	char	write the character "char" to the tape.
#
# (I'm aware that some Turing machine models allow you to write to the
# tape and move in one transition.  These programs require the new TuringDX
# processor :-))
#
# This program also times the result (We used this program as a comparative
# benchmark to compare Python's performance to other dynamic languages.
# For the curious, Turing began its life as a C++ program.)  Since most
# simulations finish in less than a second, you can have the program repeat a
# computation a specified number of times.  (and some systems (i.e. DOS)
# have low resolution timers)
################################################################################


from string import *
from sys    import exit


#---------------------------------------------------------------------------#
#				main
#---------------------------------------------------------------------------#

def main():
    from sys import argv

    if len(argv) == 3:
	count = 1

    elif len(argv) != 4:
	print 'usage:', argv[0], 'file inputstring [count]'
	exit(0)

    else:
	count = atoi(argv[3])

    turing(argv[1], argv[2], count)



#---------------------------------------------------------------------------#
#	load, execute, & time a turing machine
#---------------------------------------------------------------------------#

def turing(filename, initial_tape, count):
    from time import time

    if filename[-3:] != '.tm':
	filename = filename + '.tm'

    program = load(open(filename, 'r'))

    t1 = time()
    for i in xrange(count):
	pos, tape = execute(program, initial_tape)
    t2 = time()

    print tape
    print '%s^' % (' '*pos)

    if (t2 - t1) >= 0.1:
	print '%.1f seconds.' % (t2 - t1)



#---------------------------------------------------------------------------#
#			run the machine
#---------------------------------------------------------------------------#

def execute(program, tape):
    state = 1
    pos   = 0

    while state != 0:
	if pos < len(tape):			# read from the tape
	    char = tape[pos]
	else:
	    char = ' '

	try:
	    iw = program[(state, char)]		# get instruction word;

	except KeyError:
	    print 'No valid transition exists for state', (state, char)
	    exit(1)

	if iw[1] == 'L':		# iw[1] is operation; iw[0] is new state
	    if pos > 0:
		pos = pos - 1
	    else:
		tape = ' ' + tape

	elif iw[1] == 'R':
	    pos = pos + 1

	else:
	    new_char = iw[1][1]		# write the new character to tape
	    if pos < len(tape):
		tape = tape[:pos] + new_char + tape[pos+1:]
	    else:
		tape = tape + ' '*(pos - len(tape)) + new_char

	state = iw[0]

    return pos, tape



#---------------------------------------------------------------------------#
#	load the turing machine into memory; return it as a mapping
#---------------------------------------------------------------------------#

def load(input):
    import regex
    from regex_syntax import *

    program = {}

    _  = regex.set_syntax(RE_SYNTAX_AWK)
    re = regex.compile("<([0-9]+),'(.)'>--><([0-9]+),(L|R|'.')>$")

    lines = input.readlines()
    for lineno, line in filter(lambda pair: len(pair[1]) > 0,
				map(lambda x,y: (x+1, strip(y)),
				    xrange(len(lines)), lines)):
	if re.match(line) == -1:
	    raise SyntaxError, `lineno` + ': Bad syntax for state transition'

	state, char, new_state, operation = re.group(1, 2, 3, 4)
	program[(atoi(state), char)] = (atoi(new_state), operation)

    return program



#---------------------------------------------------------------------------#
#	strip comments and white space from state transition lines
#---------------------------------------------------------------------------#

def strip(str):
    result  = ''
    i = 0

    while i < len(str):
	if str[i] in whitespace:
	    i = i + 1

	elif str[i] == ';':
	    break

	elif str[i] == '\'':
	    result = result + str[i:i+3]
	    i = i + 3

	else:
	    result = result + str[i]
	    i = i + 1

    return result



if __name__ == '__main__':
    main()
