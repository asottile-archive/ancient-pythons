#
# module backwrd3.py
#
# backward chaining with explicit stacks;
#
# maintains 2 stacks (represented as trees,
# (binary tuples), rather than lists):
#
# 'state' stack ('and' node generator):
#     (dict, goal-list, last-goal, rule-id, state)
# 'back'  stack ('or' node generator):
#     (state, var-changes, last-rule, last-then, back)
#
# INCOMPLETE:
# this variant works, but does not yet implement
# 'not' negations, or 'how' explanations;  these 
# are straightforward (but tedious) to add: for 
# 'not', insert a '_fail_' goal into the current
# state, detect it in the main loop, and force a
# backtrack to the 'back' that existed when the
# 'not' was started;  also push a backtrack node
# that backtracks to redo a 'true' goal (and so
# succeeds);  for 'how', we need to push the 
# current proof tree list on backtrack nodes,
# and restore them when backtracking;  we also
# need to detect end of conjuncts (in nextgoal),
# and add a '()' terminator to the how list;
# ex:
# state = ({}, goals+[['_fail_']], last, rule, state) 
# back = (({},[['true']],0,'not',state), [], 0, -1, back)
# left as an exercise for the reader...
#
# note:
# there's a slight overhead to pack/unpack tuples
# in the assignments; we might get a slight 
# improvement by using 5 seperate variables
# to represent current 'state'; for ex: when
# 'nextgoal()' just goes to the next 'if' goal
# and does no climbing, we could just add 1
# to the current goal index;  also: the 'rule' 
# part of 'state' tuples is only used for 
# ask_user, and could otherwise be ignored;
####################################################




from match import *
from kbase import external
from backward import stop_proof, ask_user, input_yes
import backward; backwrd1 = backward




def backtrack(back):
    if not back:
        return (None,) * 4
    else:
        (state, changes, rule, then, back) = back
        for var, env in changes:
            env[var] = '?'
        return state, rule, then+1, back




def nextgoal(state):
    while 1:
        (dict, goals, last, rule, state) = state
        if last < len(goals)-1:
            return (dict, goals, last+1, rule, state)
        if not state:
            return None




def backward(kbase, query, *pmode):
    backwrd1.kbase = kbase
    try:
        bchain(kbase, ({}, query, 0, None, None), None, [['true']], pmode)
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
            if not report(top[0], top[1], pmode):
                return
            else:
                state, kindex, tindex, back = backtrack(back)
                continue

        (dict, goals, curr, rid, parent) = state
        first_try = (kindex == 0 and tindex == 0)
        matched = 0

        for rule in kbase[kindex:]:
            for then in rule['then'][tindex:]:
                dict2 = {}
                matched, changes = match(goals[curr], then, dict, dict2) 
                if matched:
                    back   = (state, changes, kindex, tindex, back)
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
                state, kindex, tindex, back = backtrack(back)
            else:
                if ask_user1(goals[curr], dict, known, state):
                    state, kindex, tindex = nextgoal(state), 0, 0
                else:
                    state, kindex, tindex, back = backtrack(back)





##################################################################
# build 'why' explanantions goal stack from the  
# 'state' stack (the 'return' parent goal stack);
# only done when we're about to ask user a question;
# this conversion is needed to reuse the ask_user()
# procedure in backward.py;
#
# the 'state' stack has a dual use: it serves
# as the 'AND' node generator (the 'return' stack,
# with all incomplete goals), and as the 'why' 
# explanation goal stack (we don't need two lists);
#
# note: it doesn't matter whether we list the goal
# (in parent dict), or the 'then' part (in the child
# rule dict), since the 2 terms have been 'unified'
# by match() (all free vars 'share');  we list the
# goal in the parent dict;
##################################################################




def ask_user1(goal, dict, known, state):
    why = []
    (x, x, x, rule1, state) = state
    while state:
        (dict, goals, curr, rule2, state) = state
        why = why + [(goals[curr], dict, rule1)]
        rule1 = rule2
    return ask_user(goal, dict, known, why)




print_mode = ('terms','one')



def report(binding, query, pmode):
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
        return input_yes('more solutions? ')
