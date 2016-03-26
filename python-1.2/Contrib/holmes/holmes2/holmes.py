#
# module holmes.py
#
# main module; implements interactive prompt, etc.
# see holmes/holmes.py and holmes.doc for more info;
# the '==' assignment command was removed, since it's
# too difficult to manually code kbases now (with
# discrimination trees);
##############################################################




import match
from kbase import *
import forward
import backward
for i in '34567': exec('import backwrd'+i)
import forward2




def holmes():
    print '-Holmes2 inference engine-'
    kbase = Kbase().init()                  # keeps one kbase
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

        elif x != '' and x[0] == '?' and x[1] in '134567':
            backchain = eval('backwrd'+x[1]).backward

        elif x != '' and x[0] == '+' and x[1] in '12':
            forchain = eval('forward'+x[1]).forward

        elif x[0:2] == '@=':                # load a kbase file: @- file
            kbase = Kbase().init(x[2:])
        
        elif x[0:2] == '+=':                # add a rule interactively
            kbase.add_rule(internal_rule(x[2:]))

        elif x[0:2] == '-=':
            kbase.remove_rule(x[2:])        # remove a rule by id interactive
        
        elif x[0:2] == '=@':                # save current kbase to a file
            kbase.save_rules(x[2:])

        elif x[0:2] == '@@':                # browse the kbase: !- if, mortal
            kbase.browse_pattern(x[2:])     # 1 or 2 optional args
        
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
    




