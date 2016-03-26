#
# module backwrd7.py
#
# non-backtracking version of backward.py
#
# this variant corrects the bug in backwrd2 (which
# copied variable binding stacks), by copying entire
# proof-tree-so-far, at each candidate in each choice
# point;  simply uses the 'how' linear proof trees
# already constructed for explanations, as the proof
# trees to compute (the linear form makes it easy
# to keep track of the current level's node);  
#
# this works, and avoids both backtracking and 
# generate-and-test coding (though constructing 
# candidate proof subtrees is really equivalent 
# backtracking early); see backwrd2 for more info;
#
# still suffers from these weaknesses:
# 1) very slow for large and/or proof trees;  again,
#    (x,y) cons-tree rep would speed up a little, 
#    but most time is spent copying proof dictionaries;
#
# 2) computes all solutions before any are displayed;
#    this is very inconvenient for interactive systems,
#    since all questions must be answered first;
#
# 3) 'not' negation is not exactly correct: it computes
#    _all_ possible solutions for the 'not' goal, and
#    then cecks if >= 1 solution was found;  'not' 
#    should really fail as soon as the _first_ solution
#    for the negated goal is found;  this might be 
#    implemented by adding a flag arg and extra logic
#    to OR and AND to return as soon as any 1 soln is
#    found (but we'd probably have to generate all
#    proofs for ifs[0..n-1] in order to detect the 
#    1st soln at ifs[n]);
##############################################################





from match import *
from forward import copy_dict
from backwrd4 import ask_user, report, stop_proof
import backward; backwrd1 = backward




def OR(goal, why, how, top):
    ask = 1
    res = []
    dict1 = how[top][1][1]

    for rule in kbase:
        for then in rule['then']:
            dict2 = {}
            matched, changes = match(goal, then, dict1, dict2)
            if matched:
                ask  = 0
                why2 = [(goal, dict1, rule['rule'])] + why
                how2 = how + [(goal, (rule['rule'], dict2))]
                for proof in AND(rule['if'], why2, how2, len(how)):
                    res.append(proof)

            for (var, env) in changes: 
                env[var] = '?'

    if ask and ask_user(goal, dict1, known, why):
        res = [how + [(goal, 'told')]]
    return res




def AND(goals, why, proof, top):
    if goals == []:
        return [copy_proof_tree(proof + [()])]
    else:
        res = []
        head, tail = goals[0], goals[1:]
        if head[0] == 'ask':
            head = head[1:]
        
        if head[0] == 'not':
            if OR(head[1:], why, proof, top):
                return []
            else:
                return AND(tail, why, proof + [(head, 'not')], top)

        for proof1 in OR(head, why, proof, top):
            for proof2 in AND(tail, why, proof1, top):
                res.append(proof2)
        return res




def backward(rules, query, *pmode):
    global known, kbase                                # avoid extra args
    backwrd1.kbase = rules                             # for rule browsing
    known, kbase = [['true']], rules                   # local to module
    try:
        for proof in AND(query, [], [(None, (None, {}))], 0):
            topenv = proof[0][1][1]
            report(topenv, query, pmode, proof[1:])
        print 'no (more) solutions  [backwrd7.py]'
    except stop_proof: pass




def copy_proof_tree(proof):
    copy = []
    for node in proof:
        if node == () or node[1] in ['told', 'not']:
            copy.append(node)
        else:
            copy.append((node[0], (node[1][0], copy_dict(node[1][1])) ))

    for node in copy:
        if node != () and node[1] not in ['told', 'not']:
            adjust_pointers(node[1][1], proof, copy)
    return copy




def adjust_pointers(dict, proof, copy):
    for var in dict.keys():
        if type(dict[var]) == type(()):                     # a sharing var?
            for i in range(len(proof)):       
                if proof[i] != () and proof[i][1] not in ['told', 'not']:
                    if dict[var][1] is proof[i][1][1]:          
                        dict[var] = (dict[var][0], copy[i][1][1]) 
                        break

            


#########################################################
# note: when the tree is first copied, the sharing vars
# will all be sharing the same (name, dict) python 
# objects;   they are all reset to new objs in copy;
#########################################################



