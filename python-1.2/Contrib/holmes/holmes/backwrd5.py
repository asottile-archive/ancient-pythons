#
# module backwrd5.py
#
# backward chaining inference engine;
#
# this is a variant of backwrd4.py, which 
# uses '(x,y)' cons-cell representation for
# how/why lists, rather than native lists and 
# '+'; tree list rep is upto 2 times faster;
#
# we have variants of report() and ask_user()
# here-- it might have been better to convert
# to the common list form and use backward.py
# versions of these, to avoid redundancy;
####################################################################




from match import *
from kbase import external, browse_pattern
from backward import input_yes
import backward; backwrd1 = backward




print_mode = ('terms', 'one')

stop_proof = 'stop_proof'
negation   = 'negation'

positive = ['y','Y','yes','YES']
negative = ['n','N','no','NO']





def backward(rules, query, *pmode):
    global known, kbase                               # avoid an extra args
    backwrd1.kbase = rules                            # for rule browsing
    known, kbase = [['true']], rules
    topenv = {}
    cont   = (report, (topenv, query, pmode))
    try:
        AND(query, topenv, None, cont, None)  
        print 'no (more) solutions  [backwrd5.py]'
    except stop_proof:
        return





def AND(goals, dict, why, cont, how):                  # rule 'if' part
    if goals == []:                                    # or top-level query 
        apply(cont[0], cont[1] + ((how, ()),))
    
    else:
        head, tail = goals[0], goals[1:]
        if head[0] == 'ask': 
            head = head[1:]

        if head[0] == 'not':
            try:
                OR(head[1:], dict, why, how, (fail, ()) )
            except negation: 
                return
            AND(tail, dict, why, cont, (how, (head, 'not')) )
        
        else:            
            OR(head, dict, why, how, (AND, (tail, dict, why, cont)) )





def OR(goal, dict, why, how, cont):                             # match 'then'
    rules = 0
    for rule in kbase:                                          # select rule
        for then in rule['then']:                               # and descend
            dict2 = {}
            matched, changes = match(goal, then, dict, dict2)
            if matched:
                rules = 1
                why2  = (goal, dict, rule['rule']), why
                how2  = how, (goal, (rule['rule'], dict2))
                AND(rule['if'], dict2, why2, cont, how2)
            for (var, env) in changes:
                env[var] = '?'    

    if not rules:
        if ask_user(goal, dict, known, why):
            apply(cont[0], cont[1] + ((how, (goal, 'told')),) )





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
            while why:
                (goal, dict, rule), why = why
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
        return
    else:
        print
        if input_yes('show proof ? '):
            ignore = trace_tree(proof, binding, 0)

        if input_yes('more solutions? '):
            print
            return
        else:
            raise stop_proof
    
    


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
# Change: the lists are now in (x,y) tree form,
# where the list grows to the top and right; the
# node at the end of the list is at the top, so
# we reverse it first, for simplicity:
#   (((None, a), b), c) -> (a, (b, (c, None)))
####################################################### 




def trace_tree(proof, dict, level):
    list = None
    while proof:
        (proof, node) = proof
        list = (node, list)
    trace_rev_tree(list, dict, level)




def trace_rev_tree(proof, dict, level):
    while proof[0] != ():
        ((goal, how), proof) = proof

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
            proof = trace_rev_tree(proof, how[1], level + 3)
    
    return proof[1]     




###################################################
# for 'not' -- negation by failure -- we need
# a special exception handler, to backtrack
# over all choice points in the 'not' goal
# immediately, when the 'not' goal succeeds;
# when the 'not' fails, we catch the normal
# 'backtrack' return and continue;
###################################################
 


def fail(how):  raise negation




