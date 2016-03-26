#
# module backwrd5.py
#
# backward chaining inference engine with tree list rep;
# see holmes/backwrd5.py and holmes.doc for more info;
####################################################################




from match import *
from index import Index
from kbase import external
from backward import input_yes




print_mode = ('terms', 'one')

stop_proof = 'stop_proof'
negation   = 'negation'

positive = ['y','Y','yes','YES']
negative = ['n','N','no','NO']





def backward(rules, query, *pmode):
    global known, kbase                               # avoid extra args
    kbase = rules
    known = Index().init([(['true'],['true'])])

    topenv = {}
    cont   = (report, (kbase, topenv, query, pmode))
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
    for rule in kbase.match_then(goal, dict):                   # select rule
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
        if ask_user(kbase, goal, dict, known, why):
            apply(cont[0], cont[1] + ((how, (goal, 'told')),) )





#################################################
# 'why' explanations just stack goal/rule
# at 'or' nodes at each level of the recursion
#################################################




def ask_user(kbase, goal, dict, known, why):
    fact = substitute(goal, dict)
    if known.search_unique(fact):
        return 1
    elif known.search_unique(['not'] + fact):
        return 0
    
    while 1:
        ans = raw_input('is this true: "' + external([fact]) + '" ? ')
        if ans in positive:
            known.store(fact, fact)
            return 1

        elif ans in negative:
            known.store(['not'] + fact, ['not'] + fact)
            return 0

        elif ans == 'why':
            while why:
                (goal, dict, rule), why = why
                print 'to prove', 
                print '"' + external([substitute(goal,dict)]) + '"', 
                print 'by rule', rule
            print 'this was part of your original query.'
        
        elif ans == 'browse':
            kbase.browse_pattern(raw_input('enter browse pattern: '))

        elif ans == 'stop':
            raise stop_proof

        else:
            print 'what?  (expecting "y", "n", "why", "browse", or "stop")'




##################################################
# supports 'how' explanations to justify each 
# solution; builds proof-tree representation
# during the inference process;
##################################################




def report(kbase, binding, query, pmode, proof):
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
        if input_yes(kbase, 'show proof ? '):
            ignore = trace_tree(proof, binding, 0)

        if input_yes(kbase, 'more solutions? '):
            print
            return
        else:
            raise stop_proof




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




def fail(how):  
    raise negation




