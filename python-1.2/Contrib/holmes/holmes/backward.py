#
# module backward.py
#
# backward chaining inference engine;
# using exceptions and change lists to simulate backtracking:
# always moves ahead/deeper in recursion, so choice points
# not popped on 'return';  uses python 'exceptions' stack
# as the backtrack stack, and the python call stack (and
# 1st-order function objects) for the remaining goal stack;
#
# handles ?-  man ?x, flies ?x  conjunctive queries;
# generates all bindings for query variables, and print each out;
# see holmes.doc for descriptions
#
# ex:  python holmes.py
#      holmes> @= fixit.kb
#      holmes> ?- go stereo ?p ?s
#
# exports procedure backward(); user can also set 
#       backward.print_mode
# to control the solution output format
#
# backward(kbase, query)         -> prints solns by 'print_mode'
# backward(kbase, query, None)   -> returns solns list to caller
# backward(kbase, query, <mode>) -> prints solns by <mode>
#
# <mode> is a 2-item tuple (X, Y).  
# X can be:
#   'terms'     -> show query with vars replaced
#   'vars'      -> list query variables and their values
# Y can be:
#   'one'       -> stop after each soln and interact
#   'all'       -> print all solutions without stopping
#
# note: holmes requires sharing of global variables across
# modules for rule browsing ('backward.kbase');  holmes2
# uses a cleaner scheme (it just passes 'kbase' in to 
# ask_user(), report(), input_yes());  we keep the global
# variable version here for illustration purposes;
####################################################################




from match import *
from kbase import external, browse_pattern




print_mode = ('terms', 'one')

stop_proof = 'stop_proof'
backtrack  = 'backtrack'                  # unique string objects
negation   = 'negation'

positive = ['y','Y','yes','YES']
negative = ['n','N','no','NO']





def backward(rules, query, *pmode):
    global known, kbase                               # avoid an extra args
    known, kbase = [['true']], rules
    topenv = {}
    cont   = (report, (topenv, query, pmode))

    try:
        AND(query, topenv, [], cont, [])  
    except backtrack:
        print 'no (more) solutions'
    except stop_proof:
        return





def AND(goals, dict, why, cont, how):                  # rule 'if' part
    if goals == []:                                    # or top-level query 
        apply(cont[0], cont[1] + (how + [()],))
    
    else:
        head, tail = goals[0], goals[1:]
        if head[0] == 'ask': 
            head = head[1:]

        if head[0] == 'not':
            try:
                OR(head[1:], dict, why, how, (fail, ()) )
            except negation:
                raise backtrack
            except backtrack:
                AND(tail, dict, why, cont, how + [(head, 'not')])
            
        OR(head, dict, why, how, (AND, (tail, dict, why, cont)) )





def OR(goal, dict, why, how, cont):                             # match 'then'
    rules = 0
    for rule in kbase:                                          # select rule
        for then in rule['then']:                               # and descend
            try:
                dict2 = {}
                matched, changes = match(goal, then, dict, dict2)
                if matched:
                    rules = 1
                    why2  = [(goal, dict, rule['rule'])] + why
                    how2  = how + [(goal, (rule['rule'], dict2))]
                    AND(rule['if'], dict2, why2, cont, how2)

            except backtrack: 
                pass                                        # try next rule

            for (var, env) in changes:
                env[var] = '?'                              # reset vars

    if not rules:
        if ask_user(goal, dict, known, why):                # ask goal
            apply(cont[0], cont[1] + (how + [(goal, 'told')],) )
   
    raise backtrack       # all rules failed or answer='no'





#################################################
# 'why' explanations just stack goal/rule
# at 'or' nodes at each level of the recursion
#################################################




def ask_user(goal, dict, known, why):
    fact = substitute(goal, dict)
    if fact in known:
        return 1
    elif (['not'] + fact) in known:
        return 0
    
    while 1:
        ans = raw_input('is this true: "' + external([fact]) + '" ? ')
        if ans in positive:
            known.append(fact)
            return 1

        elif ans in negative:
            known.append(['not'] + fact)
            return 0

        elif ans == 'why':
            for (goal, dict, rule) in why:
                print 'to prove', 
                print '"' + external([substitute(goal,dict)]) + '"', 
                print 'by rule', rule
            print 'this was part of your original query.'
        
        elif ans == 'browse':
            browse_pattern(kbase, raw_input('enter browse pattern: '))

        elif ans == 'stop':
            raise stop_proof

        else:
            print 'what?  (expecting "y", "n", "why", "browse", or "stop")'




##################################################
# supports 'how' explanations to justify each 
# solution; builds proof-tree representation
# during the inference process;
##################################################




def report(binding, query, pmode, proof):
    if not pmode:
        pmode = print_mode                         # use current global mode
    else:
        pmode = pmode[0]
        if pmode == None:
            return binding                         # return solns to caller
                                                   # else use pmode passed
    if binding == {}:
        print 'yes: (no variables)'
    else:
        if pmode[0] == 'vars':
            print 'yes: ', 
            for var in binding.keys():
                print var, '=', binding[var], ' ',
            print
        else:
            print 'yes: ' + external(substitute(query, binding))
    
    if pmode[1] == 'all':
        raise backtrack
    else:
        print
        if input_yes('show proof ? '):
            ignore = trace_tree(proof, binding, 0)

        if input_yes('more solutions? '):
            print
            raise backtrack
        else:
            raise stop_proof
  



def input_yes(prompt):
    while 1:
        ans = raw_input(prompt)
        if ans in positive:
            return 1
        elif ans in negative:
            return 0
        elif ans == 'browse':
            browse_pattern(kbase, raw_input('enter browse pattern: '))
        else: 
            print 'what?  (expecting "y", "n", or "browse")'
    
    



#######################################################
# this routine expects proof trees in this form:
#
#    [ (goal0, 'told'),
#      (goal1, (rule-id, dict)), 
#          (goal1.1, 'told'), 
#          (goal1.2, 'told'), 
#          ()
#      (goal2, (rule-id, dict)), 
#          (goal2.1, how),
#          (goal2.2, how),
#          (),
#      ()  
#    ]
#
# the '(rule-id dict)' proof can be a pythin tuple or 
# list (its a list in backwrd2 to allow setting the 
# dict later), and must be followed by the proof
# trees of each goal in the rule's 'if' part;
#
# this linear form is convenient for the purely forward
# progression on the backtracking backward();  it's
# not as important to be linear in the non-backtracking
# version (we could build nested proof trees instead);
# trees are built top-down in backward chaining (or
# 'step-wise': we add to the list at each goal/node);
####################################################### 




def trace_tree(proof, dict, level): 
    while proof[0] != ():
        (goal, how), proof = proof[0], proof[1:]

        print ' ' * level,
        print '"' + external([substitute(goal, dict)]) + '"',

        if how == 'not':
            print 'by failure to prove', \
                     '"' + external([substitute(goal[1:], dict)]) + '"'
    
        elif how == 'told':
            if goal == ['true']:
                print 'is an absolute truth'
            else:
                print 'by your answer'
 
        else:
            print 'by rule', how[0]
            proof = trace_tree(proof, how[1], level + 3)
    
    return proof[1:]     




###################################################
# for 'not' -- negation by failure -- we need
# a special exception handler, to backtrack
# over all choice points in the 'not' goal
# immediately, when the 'not' goal succeeds;
# when the 'not' fails, we catch the normal
# 'backtrack' exception and continue;
#
# note: in this code, the 'raise backtrack'
# goes back to an older choice point, lower
# on the stack (not in the same 'try' stmt):
#    try:
#        OR(head[1:], ..., (fail, ()) )
#    except negation:
#        raise backtrack
#    except backtrack:
#        AND(tail, ...)
###################################################
 


def fail(how):  raise negation




