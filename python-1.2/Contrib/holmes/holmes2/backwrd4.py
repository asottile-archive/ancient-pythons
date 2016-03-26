#
# module backwrd4.py
#
# backward chaining inference engine without exceptions;
# see holmes/backwrd4.py and holmes.doc for more info;
####################################################################




from match import *
from index import Index
from backward import ask_user, stop_proof




print_mode = ('terms', 'one')
negation   = 'negation'

positive = ['y','Y','yes','YES']
negative = ['n','N','no','NO']





def backward(rules, query, *pmode):
    global known, kbase                                # avoid extra args
    kbase = rules
    known = Index().init([(['true'],['true'])])

    topenv = {}
    cont   = (report, (kbase, topenv, query, pmode))
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
    for rule in kbase.match_then(goal, dict):                   # select rule
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
        if ask_user(kbase, goal, dict, known, why):
            apply(cont[0], cont[1] + (how + [(goal, 'told')],) )




def fail(how):  
    raise negation




def report(kbase, topenv, query, pmode, how):
    import backward
    try:
        backward.report(kbase, topenv, query, pmode, how)
    except backward.backtrack:
        return
    # else raises stop_proof


