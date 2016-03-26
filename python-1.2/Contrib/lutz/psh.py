#
# Python command shell utility
#
# simplifies debugging, editing, etc;
# augments normal Python commmand line;
# cmd history: redundant if edline built;
#
# use:  python psh.py
#       python; import psh; psh.go(); help
#
# TODO:
# - cmd history scrolling via arrow keys
# - arbitrary '$' aliases/replacements
# - make it a class, so can use in other 
#   apps (call self.handler, not python())
# - see about using pdb's command class
#   so shell cmds recognized while in pdb
# - 'edit' (but not 'vi') runs out of 
#   memory under windows (not under DOS)
#############################################



from os import *
from string import *


editor   = 'vi'         # 'edit'
memory   = 20           # settable: % shell.editor = 'vi'
histnum  = 0            # retain all settings for next go()
history  = []         
prompter = '%'          
aliases  = []




def interact():
    while 1:
        cmd = raw_input(prompter + ' ')
        cmd = prescan(cmd)
        if cmd == 'quit':
            break
        execute(cmd)
    



def execute(cmd):
    global history, histnum
    args = split(cmd)
    if not args:                    # empty line or all blanks
        return                      # else >= 1 word on line
    
    if shell_command(args[0]):
        func = eval(args[0])              # get function for command
        try: 
            func(args[1:])                # null if no args[1:]
        except:
            print 'bad shell command'     # any errors come here

    else:
        try:
            python(cmd)                   # try as python command
        except:
            print 'bad command:', args[0]

    if args[0] != 're':
        histnum = histnum+1
        history = history[-(memory-1):] + [(histnum, cmd)]




##################################################                
# see notes at bottom of file;
##################################################



def shell_command(name): 
    return (name in help_dir.keys())



def python(cmd):
    import __main__
    exec(cmd, __main__.__dict__, __main__.__dict__)




#####################################################
# one function per keyword command; add to help too
#####################################################



def quit(args):
    raise NameError          # superfluous args



def prompt(args):        
    global prompter
    prompter = args[0]
        


def pwd(args):
    print getcwd()



def cd(args): 
    if not args:
        chdir()
    else:
        chdir(args[0])
    print getcwd()



def ls(args): 
    if not args:
        t = system('ls')                # listdir('.')
    else:
        t = system('ls ' + args[0])     # listdir(args[0])
    


def ed(args):
    t = system(editor + ' ' + args[0])



def os(args):
    t = system(join(args))                  # ex: os cp shell.py a:
                                            # 'os' alone starts shell 


def fix(args):                            
    import sys                              # ex: fix holmes
    module = args[0]
    ed([module + '.py'])                    # assumes in cwd/'.'
    if module in sys.modules.keys():
        python('reload(' + module + ')')    # reload in __main__
    else:
        python('import ' + module)          # first load in __main__



def db(args):
    import pdb
    pdb.run(join(args))                     # ex: db shell.help(['ls'])
                                            # pdb runs cmd in __main__


def hi(args):
    for (number, command) in history:
        print number, '=>', command
         


def re(args):
    if not args:
        repeat = history[len(history)-1][1]
    else:
        try:
            number = eval(args[0])                    # fail if non-num
            for (num, cmd) in history: 
                if num == number: 
                    repeat = cmd; 
                    break
            else: raise NameError                     # number not found
        except:
            prefix = join(args)
            history.reverse()
            for (num, cmd) in history:
                if cmd[:len(prefix)] == prefix:
                    repeat = cmd
                    history.reverse()
                    break
            else:
                history.reverse()
                print 'bad history command number'
                return
    
    print 'redo:', repeat
    execute(repeat)                      # recursive call




def src(args):
    # import sys
    # save = (sys.stdin, sys.stdout)
    file = open(args[0], 'r')                    # open can fail
    while 1:
        cmd = file.readline()                    # read can fail
        if not cmd: 
            break
        cmd = prescan(cmd)
        if cmd == 'quit':
            break
        if cmd: print '[' + cmd + ']...'
        execute(cmd)
    file.close()




def equ(args):
    if not args:
        for (patt, subst) in aliases:
            print `patt`, '=>', `subst + ' '`
    else:
        global aliases                                     # (from, to)
        aliases = [(args[0], join(args[1:]))] + aliases    # to can be a list 
        



##########################################################
# currently only allows aliase name to be at the front
# of the command line, not embedded in it (no '$' subst);
# cmd pattern must be followed by a blank iff the patt
# is not a special char, and the cmd contains args;
# this stops 'quit' from becoming 'quit uit' when 'q'
# has been aliased to 'quit';
##########################################################



def prefix(cmd, patt):
    if cmd[:len(patt)] == patt:
        if patt[0] not in letters:
            return 1
        if len(cmd) == len(patt): 
            return 1
        if cmd[len(patt)] in whitespace: 
            return 1
    return 0



def prescan(cmd):
    cmd = strip(cmd)               # strip blanks for 'quit' test
    if cmd and cmd[0] == '#':      # allow comments in src files
        return ''
    
    for (patt, subst) in aliases:
        if prefix(cmd, patt):
            cmd = strip(subst + ' ' + cmd[len(patt):])     # allow '!' for 're '
            print 'equ:', cmd                              # alloq 'q' for quit
            break

    return cmd            




##################################################    
# help_dir also serves to identify shell   
# command names (distinct from python cmds);
##################################################




help_dir = \
{   'pwd':      ('',               'print current directory'),         \
    'ls':       ('<dir>?',         'list contents of dir'),            \
    'cd':       ('<dir>?',         'change current directory'),        \
    'ed':       ('<file>?',        'edit a file (shell.editor)'),      \
    'os':       ('<cmd>?',         'send command to system'),          \
    'db':       ('<expr>?',        'run expr under pdb debugger'),     \
    'fix':      ('<module>',       'edit and import|reload module'),   \
    'prompt':   ('<str>',          'change the prompt string'),        \
    'hi':       ('',               'prior command history list'),      \
    're':       ('[<num>|<str>]?', 'repeat a prior command (see hi)'), \
    'quit':     ('',               'exit the shell'),                  \
    'help':     ('<cmd>?',         'describe one|all commands'),       \
    'equ':      ('[<str> <val>]?', 'replace/aliase <str> with <val>'), \
    'src':      ('<file>',         'read commands from a text file')   \
}




help_examples = \
{   'ls':       'ls, ls ../benches/holmes',               \
    'cd':       'cd ../benches',                          \
    'ed':       'ed, ed shell.py',                        \
    'os':       'os, os cp shell.py a:',                  \
    'db':       'db shell.help([\'db\'])',                \
    'fix':      'fix shell',                              \
    'prompt':   'prompt psh>',                            \
    're':       're 12, re x =, re db. [equ ! re, !fix]', \
    'equ':      'equ, equ ! re, equ save os cp *.py a:',  \
    'src':      'src script.txt'                          \
}




def help(args):
    if args:
        try:
            desc = help_dir[args[0]]
            print 'Command:    ', args[0]
            print 'Arguments:  ', desc[0]
            print 'Description:', desc[1]
            if args[0] in help_examples.keys():
                print 'Examples:   ', help_examples[args[0]]
        except:
            print 'unknown help command'

    else:
        print 'Available commands...\n'
        keys = help_dir.keys()
        keys.sort()
        for x in keys:
            print ljust(x + ' ' + help_dir[x][0], 18), help_dir[x][1]
        print '\nOther commands are run by the Python interpreter in __main__'
        print 'Type \'help <cmd>\' for more information on a specific command\n'




############################################
# run shell; 'shell.go()' restarts is again
# note: 'shell' is not available in __main__
# yet, until this file is completely read,
# so you can't 'db' shell stuff until you
# 'quit' and call 'shell.xxx()' directly;
#
# load (src's) '.PshInit' if present in cwd;
# should also ckeck home dir too;  useful
# for canned 'equ' aliase commands, 'os' 
# and 'prompt' commands, etc;
############################################




def go():
    print '-Python command shell-'
    try:
        src(['.PshInit'])
        print 'loaded .PshInit'
    except:
        print '.PshInit file not found'
    interact()
    print 'command shell exit.'


go()






##################################################
# notes;
# eval() succeeds for python cmds too
# exec() runs with local=function in 'shell'
# 'import *' adds os/string funcs to 'shell'
#
# def shell_command(name):
#     import shell
#     return (name in shell.__dict__.keys())
##################################################    
# import sys
# exec(join(args), \
#         sys.modules['__main__'].__dict__, \
#         sys.modules['__main__'].__dict__)
#
# 'x' = sys.modules['__main__'].x
# 'x' = sys.modules['__main__'].__dict__['x']
##################################################


