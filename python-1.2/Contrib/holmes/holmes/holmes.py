#
# module holmes.py
#
# main module; implements interactive prompt, etc.
# users need only import this module to get the whole system:
#       >>> from holmes import holmes
#       >>> holmes()
#
#       C> python holmes.py
#       holmes>
#
# the holmes() command line interpreter is mostly fluff, 
# since users can invoke forward() and backward() and set kbase 
# variables interactively at the normal Python command line:
#       >>> kl = [...]
#       >>> forward(k1, [['man', 'socrates']])
#       >>> backward(k1, [['mortal', '?x']])
#
#       holmes> == [...]
#       holmes> +- man socrates
#       holmes> ?- mortal ?x
#
# using multiple kbase's may be easier in the python command
# line, instead of holmes() (which keeps a single kbase list);
##############################################################




import match
from kbase import *
import forward
import backward
for i in '234567': exec('import backwrd'+i)
import forward2





def holmes():
    print '-Holmes inference engine-'
    kbase = []                              # keeps one kbase
    backchain = backward.backward           # default back chainer
    backwrd1  = backward
    forchain  = forward.forward             # default fwd chainer
    forward1  = forward

    while 1:
        x = raw_input('holmes> ')

        if x[0:2] == '+-':                  # start forward chaining
            facts = internal(x[2:])         # +- man plato, woman wanda
            forchain(kbase, facts)
        
        elif x[0:2] == '?-':                # start backward chaining
            goal = internal(x[2:])          # ?- mortal ?x
            backchain(kbase, goal)

        elif x[0:2] == '++':                # forward chain, with 'filter'
            facts = internal(x[2:])         
            facts, filter = facts[0:len(facts)-1], facts[len(facts)-1]
            forchain(kbase, facts, filter)

        elif x[0:2] == '??':                # backward, with print mode
            goals = internal(x[2:])
            size = len(goals)
            goal = goals[0:size-2]
            backchain(kbase, goal, (goals[size-2][0], goals[size-1][0]))

        elif x != '' and x[0] == '?' and x[1] in '1234567':
            backchain = eval('backwrd'+x[1]).backward

        elif x != '' and x[0] == '+' and x[1] in '12':
            forchain = eval('forward'+x[1]).forward

        elif x[0:2] == '@=':                # load a kbase file: @- file
            kbase = load_rules(x[2:])
        
        elif x[0:2] == '==':                # set kbase directly: == []
            kbase = eval(x[2:])             # also: !- k1 = [..], == k1
        
        elif x[0:2] == '+=':                # add a rule interactively
            kbase.append(internal_rule(x[2:]))

        elif x[0:2] == '-=':
            remove_rule(x[2:])              # remove a rule interactively
        
        elif x[0:2] == '=@':                # save current kbase to a file
            save_rules(kbase, x[2:])

        elif x[0:2] == '@@':                # browse the kbase: !- if, mortal
            browse_pattern(kbase, x[2:])    # 1 or 2 optional args
        
        elif x[0:2] == '!-':                # run a statement: !- kbase = k1
            exec(strip(x[2:]))              # will also print an expr value
     
        elif x == 'help':
            list_commands()                 # command help

        elif x == 'stop':                   # exit command line
            break
        
        elif x != '':                       # ignore blank lines
            print 'what?'




def list_commands():
    print 'I understand these command forms:'
    print
    for x in \
        ['+- fact, fact..    --forward chain',             \
         '?- goal, goal..    --backward chain',            \
         '++ fact,.., filter --forward, with filter',      \
         '?? goal,.., x,y    --backward, with print mode', \
         '?n   (n=1..7)      --use back chainer variant',  \
         '+n   (n=1..2)      --use forward chain variant', \
         ' ',                                              \
         '@= file            --load a kbase file',         \
         '== [{..},{..}]     --set kbase list',            \
         '+= rule x if y..   --add a rule to kbase',       \
         '-= id              --delete kbase rule',         \
         '=@ file            --save kbase to file',        \
         '@@ part, value     --browse kbase',              \
         ' ',                                              \
         '!- statement       --run Python stmt or expr',   \
         'help               --get this listing',          \
         'stop               --exit holmes',               \
         ' '                                               \
        ]: print x                                   




holmes()     # run shell immediately when module is imported
             # note: code below this not yet available in holmes shell





#############################################################
# here, we define 2 ways to redirect input/output, 
# from files and strings;   neither of these is 
# necessary on most platforms;  just use:
#   python holmes.py < file1 > file2
#
# the methods here would be useful for doing more,
# for example, logging the i/o of an interactive session;
# (we can call stdin.read, etc., from the i/o classes
# we provide, to augment them;  we can also pass
# stdin.read, etc., around like function objects)
#
# FILE I/O.....
# in unix, we can redirected stdin/out to test holmes();
# to allow this on other platforms, we manually redirect  
# the 2 streams here, for testing (they are user-visible
# file objects in std module 'sys' in python);  we could
# also change holmes() to check if running interactively,
# and read/write file objects via their i/o methods directly
# if not, but this wouldn't redirect the output of results
#
#   ex: test()            use normal stdin/out (poss piped)
#       test('f1')        use f1 as stdin
#       test('f1', 'f2')  use f1 as stdin, and f2 as stdout
#
#
#   ex: 'f1' contents:
#       += rule x if fast ?x then optimized ?x
#       +- fast scheme
#       ?- optimized scheme
#       yes
#       stop
#
#
# STRING I/O.....
# since 'print', 'raw_input', etc., must already use file 
# object i/o methods internally, *any* object with methods
# '.read', '.write', etc. would be able to serve as an i/o 
# source, by setting sys.stdin/out to them;  we use this 
# fact here to define a class that allows strings to be
# used for program input and output;  this method could
# also be used to implement 'sscanf', 'sprintf', etc.
# [though these are avialable n Python as 'eval(<string>',
# and backquotes (`expr`), respectively]
#
#   ex: test_strings('+= rule 1 if alive ?x then eat ?x\nstop\n')
#   test_strings('@=ttt5\n+- man socrates\nstop\n')
#       test_strings('!- kbase\n?- mortal plato\nyes\nstop\n')
#
# note: slices substitute the actual upper/lower bounds,
# when the bounds are out-of-range, and work right on 
# an empty sequence (zero elements);  because of this, 
# the Input class read methods handle end-of-string
# right: 'size' can be > len(string), and we keep
# returning EOF ('') after the string is exhasted:
#    ''[:n]  ==  ''[n:]  ==  ''
#############################################################




import sys



def redirect(files):
    global save_in, save_out
    if files:
        import sys
        input = open(files[0], 'r')                 # a file object/instance
        save_in   = sys.stdin
        sys.stdin = input                           # preopened file obj
        if len(files) == 2:
            output = open(files[1], 'w')
            save_out   = sys.stdout
            sys.stdout = output



def restore(files):
    global save_in, save_out
    if files:
        sys.stdin.close()
        sys.stdin = save_in                         # restore terminal i/o
        if len(files) == 2:
            sys.stdout.close()
            sys.stdout = save_out



def test(*files):                   # 0 args = interactive
    redirect(files)                 # 1 arg  = stdin name
    holmes()                        # 2 args = stdin, stdout
    restore(files)




#
# using strings for i/o, via classes
#


class Input:
    def init(self, string):
        self.data = string; return self
    
    def read(self, *size):
        if not size:
            res, self.data = self.data, ''
        else:
            res, self.data = self.data[:size], self.data[size:]
        return res
    
    def readline(self):
        if '\n' in self.data:
            where = index(self.data, '\n')
            res, self.data = self.data[:where+1], self.data[where+1:]
        else:
            res, self.data = self.data, ''
        return res



class Output:
    def init(self):
        self.data = ''; return self
    def flush(self):
        return None
    def write(self, str):
        self.data = self.data + str




def test_strings(input):
    source = Input().init(input)
    target = Output().init()

    prior_in, prior_out   = sys.stdin, sys.stdout       # save file objects
    sys.stdin, sys.stdout = source, target              # use class objects
    
    holmes()

    sys.stdin, sys.stdout = prior_in, prior_out
    return target.data                                  # return output str
    






##################################################################
# note: since python prints a statement's value if it 
# is not used, we can pass an expression to exec() to
# print it's value;  eval(<expr>) need not be used
# to print expr values from the command shell: 
# '!! expr' == '!- expr', but '!! stmt' fails
#
#        elif x[0:2] == '!!':   # print an expr value: !! kbase
#            print eval(x[2:])         
##################################################################        




