#
# module backwrd2.py
#
# non-backtracking version of backward.py
#
# INCOMPLETE:
# there is a subtle bug in thuis version (see end of this
# program);  we really need to make copies of entire
# proof-trees-so-far at each step, not just the stack
# configuration above the current level;  this is costly,
# but seems the only way to avoid the generate-and-test,
# or explicit stack backtracking versions;
#     >>see backwrd7.py for a corrected version<<
#
# copies candidate binding environment stack configurations
# at OR nodes, and intersects/expands them at AND nodes
#
# shortcomings:
# 1) very slow (compared to backtracking);  the dict 
# stk copying is a significant overhead (it would be less
# if dict copying were a built-in operation);
#
# 2) this could be improved (a little) by using the tree 
# representation for lists (used in backwrd3.py) when 
# extending the dict stack in recursion;  however, we still 
# must make complete dict stk copies at the end of each 
# conjunction, so the tree rep will only speed up passing 
# the stack ahead in recursion;  we'd also get a little 
# speed by using the tree rep for the 'how' and 'why' lists;
#
# 3) finds _all_ solutions, before presenting any to the 
# user;  this makes it seem slower, and makes it impossible
# to stop the proof after finding a reasonable solution;
#
# 3) explanations ('how') require that each dict for a
# rule's goals be copied in each candidate proof tree, 
# since bindings are undone as the recursion unfolds;
# we simply pick up the copy already in the dict stack;
#
# 4) this is very tricky code-- we must adjust cross-bound
# free variables to point to the dict's in the stk copy;  
# we might instead copy the dict stack as we go ahead 
# in the recursion instead of at the end of a conjunction;
# this may avoid the sharing var pointer adjustments, and
# the extra step for 'how' dicts, but may not be possible,
# since we traverse the and/or tree depth-first-- we need
# new complete stack copies at each alternative soln at a
# low/nested level -> would essentially need to copy 
# _entire_ stack before each match() call, which is really
# not much better (and probably worse) than copying it
# end of a successful conjunct;
##############################################################




from match import *
from backward import ask_user, report, stop_proof, backtrack
from forward import copy_dict
import backward; backwrd1 = backward




def OR(goal, stack, why, how):
    ask = 1
    res = []

    for rule in kbase:
        for then in rule['then']:
            dict2 = {}
            matched, changes = match(goal, then, stack[0], dict2)
            if matched:
                ask  = 0
                why2 = [(goal, stack[0], rule['rule'])] + why
                how2 = how + [(goal, [rule['rule'], '?'])]
                below = AND(rule['if'], [dict2] + stack, why2, how2)
                for (stack2, proof) in below:
                    proof[len(how2)-1][1][1] = stack2[0]
                    res.append((stack2[1:], proof))

            for (var, env) in changes: 
                env[var] = '?'

    if ask and ask_user(goal, stack[0], known, why):
        res = [(stack, how + [(goal, 'told')])]
    return res




def AND(goals, stack, why, how):
    if goals == []:
        return [(copy_dict_stack(stack), how + [()])]
    else:
        res = []
        head, tail = goals[0], goals[1:]
        if head[0] == 'ask':
            head = head[1:]
        
        if head[0] == 'not':
            if OR(head[1:], stack, why, how):
                return []
            else:
                return AND(tail, stack, why, how + [(head, 'not')])

        for (stack1, how1) in OR(head, stack, why, how):
            for (stack2, how2) in AND(tail, stack1, why, how1):
                res.append((stack2, how2))
        return res




##############################################################
# backwrd2 constructs all solutions at once, before any are
# reported;  since report() raises 'backtrack' to generate
# more solutions, we catch it here, and just goto the next
# solution on the list returned by AND();  'stop_proof' can
# be raised during ask_user(), or inside report() if no more
# solutions are desired;
##############################################################




def backward(rules, query, *pmode):
    global known, kbase                                # avoid extra args
    backwrd1.kbase = rules                             # set for browsing
    known, kbase = [['true']], rules                   # local to module
    try:
        for (stack, proof) in AND(query, [{}], [], []):
            try:
                report(stack[0], query, pmode, proof)
            except backtrack: 
                pass
        print 'no (more) solutions  [backwrd2.py]'
    except stop_proof: pass




###########################################################
# copy current binding stack configuration as a 
# candidate solution;  some subtle problems:
#
# 1) must reset sharing/cross-bound variable refs to dicts
# in the old stack, to their copied counterparts in the
# new stack, or else the var shares with a variable in
# the old stack (which is the stack passed ahead in
# recursion, and will be eventually freed, losing any
# bindings made later); ex:
#
#           rule 1 if b ?x then a ?x.
#           rule 2 if d 1, c ?x then b ?x.      
#           rule 3 if true then c 1, d 1.
#
# when 'd 1' succeeds, we make a copy of the binding stack,
# where rule 2's ?x references/shares rule 1's ?x;  but in 
# the copy (if we dont adjust ptrs), rule 2's ?x ref's the 
# rule 1 dict in the OLD STACK, not the rule 1 dict in the 
# NEW COPY STACK;  so when 'c ?x' binds rule 2's ?x to 1,
# it binds rule 1's ?x in the OLD STACK to 1-- the binding
# is not made in the copy stack, and so is not in the solution
# (the soln would be 'a ?', when it should be 'a 1'); 
#
# 2) must build soln stack first (before adjusting car dict 
# pointers), since we can't guarantee that all bindings are 
# from newer (lower) to older (higher) free variables-- [we'd 
# need to compare relative stack height in match() to guarantee 
# this]: ex:           
#           
#           rule 1 if b ?x then a ?x.
#           rule 2 if c ?x ?y, d ?y then b ?x.
#           rule 3 if true then c ?x ?x.
#           rule 4 if true then d 1.
#
# binds rule 1's ?x to rule 2's ?y (older to newer)-- the result
# is 'a 1' (if we didn;t allow for older->newer bindings in our
# stack copying, we'd get 'a ?', since the binding is lost);
#
# 3) weirder still: because we can't guarantee that sharing
# vars wont be oriented older->newer (lower->higher) in the
# dict stack, we really have to copy the entire stack each
# time, including any growth that took place earlier and
# has been popped, since the older var may make multiple
# bindings to the newer var later on;  ex:
#           
#           rule 1 if b ?x, d ?x then a ?x.
#           rule 2 if c ?x ?y then b ?x.
#           rule 3 if true then c ?x ?x.
#           rule 4 if true then d 1, d 2.
#
# here, ?x in rule1 gets bound to ?y in rule 2 (as above),
# and rule 2's stack node gets popped when it returns to
# rule 1 (with multiple soln stacks for the 'b ?x' goal);
# now, rule1 computes 2 soln's for 'd ?x', and therefore 
# 2 dictionaries for rule 2, already popped;  if we don't
# also copy rule 2's popped dict as part of the soln, we
# wind up with 2 'a ?' solutions, since the binding for
# ?x in rule 2's dict is undone after it is match()'ed.
#
#           rule 1 if b ?x then a ?x.
#           rule 2 if c ?x ?y, d ?y then b ?x.
#           rule 3 if true then c ?x ?x.
#           rule 4 if true then d 1, d 2.
#
# in this varient, we get the right solns ('a 1', 'a 2'),
# but the 'how' explanations are wrong: all but the topmost
# level show the 'a 2' bindings in the explanation, since 
# the 'd 2' binding is the last in effect;
#
# this problem seems insurmountable in the stack copying 
# paradigm: we really have a _TREE_ of dicts, and must
# copy the entire proof TREE thus far, at the end of each 
# conjunct or before each match() call;  our algorithm
# must compute all possible proof trees, not stack 
# configurations;
###########################################################




def copy_dict_stack(stack):
    copy = []
    for dict in stack:
        copy.append(copy_dict(dict))

    for new in copy:
        for var in new.keys():
            value = new[var]
            if type(value) == type(()):                   # a sharing var?
                for i in range(len(stack)):               # refs dict in old?
                    if value[1] is stack[i]:              # not '=='
                        new[var] = (value[0], copy[i])    # to newstk dict 
                        break
    return copy


