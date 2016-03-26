#
# module backwrd3.py
#
# backward chaining with explicit stacks;
# see holmes/backwrd3.py and holmes.doc for more info;
#
# for the index tree optimization, we need to 
# also push the set of possibly-matching
# rules on each backtrack stack node;
# we could get rid of 'kindex' by pushing
# the remaining rules in rule_set;
####################################################




from match import *
from index import Index
from kbase import external
from backward import stop_proof, ask_user, input_yes




def backtrack(back):
    if not back:
        return (None,) * 5
    else:
        (state, changes, rule, then, rule_set, back) = back
        for var, env in changes:
            env[var] = '?'
        return state, rule, then+1, rule_set, back




def nextgoal(state):
    while 1:
        (dict, goals, last, rule, state) = state
        if last < len(goals)-1:
            return (dict, goals, last+1, rule, state)
        if not state:
            return None




def backward(kbase, query, *pmode):
    known = Index().init([(['true'],['true'])])
    try:
        bchain(kbase, ({}, query, 0, None, None), None, known, pmode)
    except stop_proof: 
        pass




def bchain(kbase, state, back, known, pmode):
    top = state
    kindex, tindex = 0, 0

    while 1:
        if kindex == None:
            print 'no (more) solutions  [backwrd3.py]'
            return

        if state == None:
            if not report(kbase, top[0], top[1], pmode):
                return
            else:
                state, kindex, tindex, rule_set, back = backtrack(back)
                continue

        (dict, goals, curr, rid, parent) = state
        matched = 0        
        
        first_try = (kindex == 0 and tindex == 0)
        if first_try:
            rule_set = kbase.match_then(goals[curr], dict)

        for rule in rule_set[kindex:]:
            for then in rule['then'][tindex:]:
                dict2 = {}
                matched, changes = match(goals[curr], then, dict, dict2) 
                if matched:
                    back   = (state, changes, kindex, tindex, rule_set, back)
                    state  = (dict2, rule['if'], 0, rule['rule'], state)
                    kindex, tindex = 0, 0
                    break
                else:
                    for var, env in changes: env[var] = '?'
                    tindex = tindex+1
            
            if matched: break
            kindex, tindex = kindex+1, 0

        if not matched: 
            if not first_try:
                state, kindex, tindex, rule_set, back = backtrack(back)
            else:
                if ask_user1(kbase, goals[curr], dict, known, state):
                    state, kindex, tindex = nextgoal(state), 0, 0
                else:
                    state, kindex, tindex, rule_set, back = backtrack(back)





def ask_user1(kbase, goal, dict, known, state):
    why = []
    (x, x, x, rule1, state) = state
    while state:
        (dict, goals, curr, rule2, state) = state
        why = why + [(goals[curr], dict, rule1)]
        rule1 = rule2
    return ask_user(kbase, goal, dict, known, why)




print_mode = ('terms','one')



def report(kbase, binding, query, pmode):
    if not pmode:
        pmode = print_mode                         # use current global mode
    else:
        pmode = pmode[0]
    
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
        return 1
    else:
        return input_yes(kbase, 'more solutions? ')
