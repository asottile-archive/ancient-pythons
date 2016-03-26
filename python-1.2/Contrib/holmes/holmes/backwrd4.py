#
# module backwrd4.py
#
# backward chaining inference engine;
# 
# this is a variant of backward.py, which implements 
# backtracking by simply 'returning' to OR node 
# generators;  still uses Python call stack for
# both AND and OR node generators, by always 
# going deeper in recursion (never returning)
# while the current proof tree is succeeding;
#
# this is simply the 'generate and test' paradigm:
# OR() is the generator, and AND() is the tester 
# of all remaining goals;
#
# in retrospect, there's no reason to raise exceptions
# to return to an OR node (choice point) level;  we
# just return here;  the only disadvantage is that 
# we also return to non choice-point nodes where the
# user was queried (which immediately return to an
# earlier choice-point level);  we still keep the 
# stop_proof and negation exceptions, to end the proof
# when report() finds the user not wanting more solns,
# and for 'not' implementation;
####################################################################




from match import *
from backward import ask_user, stop_proof
import backward; backwrd1 = backward




print_mode = ('terms', 'one')
negation   = 'negation'

positive = ['y','Y','yes','YES']
negative = ['n','N','no','NO']





def backward(rules, query, *pmode):
    global known, kbase                               # avoid an extra args
    backwrd1.kbase = rules                            # set for browsing
    known, kbase = [['true']], rules
    topenv = {}
    cont   = (report, (topenv, query, pmode))
    try:
        AND(query, topenv, [], cont, [])  
        print 'no (more) solutions  [backwrd4.py]'
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
                return
            AND(tail, dict, why, cont, how + [(head, 'not')])
        
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
                why2  = [(goal, dict, rule['rule'])] + why
                how2  = how + [(goal, (rule['rule'], dict2))]
                AND(rule['if'], dict2, why2, cont, how2)
            for (var, env) in changes:
                env[var] = '?'    

    if not rules:
        if ask_user(goal, dict, known, why):
            apply(cont[0], cont[1] + (how + [(goal, 'told')],) )





###################################################
# for 'not' -- negation by failure -- we need
# a special exception handler, to backtrack
# over all choice points in the 'not' goal
# immediately, when the 'not' goal succeeds;
# when the 'not' fails, we catch the normal
# 'backtrack' return and continue;
###################################################
 



def fail(how):  raise negation




def report(topenv, query, pmode, how):
    try:
        backwrd1.report(topenv, query, pmode, how)
    except backwrd1.backtrack:
        return
    # else raises stop_proof


