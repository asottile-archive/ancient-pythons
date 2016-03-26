#
# module backwrd7.py
#
# non-backtracking version of backward.py
# see holmes/backwrk7.py and holmes.doc for more info;
##############################################################





from match import *
from index import Index
from forward import copy_dict, certainty
from backward import ask_user, stop_proof




def OR(goal, why, how, top):
    ask = 1
    res = []
    dict1 = how[top][1][1]

    for rule in kbase.match_then(goal, dict1):
        for then in rule['then']:
            then, cft = certainty(then)
            dict2 = {}
            matched, changes = match(goal, then, dict1, dict2)
            if matched:
                ask  = 0
                why2 = [(goal, dict1, rule['rule'])] + why
                how2 = how + [(goal, (rule['rule'], dict2))]
                for (proof, cfi) in AND(rule['if'], why2, how2, len(how)):
                    res.append((proof, cft * cfi))

            for (var, env) in changes: 
                env[var] = '?'

    if ask: 
        cf = ask_user(kbase, goal, dict1, known, why)
        if cf:
            res = [(how + [(goal, 'told')], cf)]
    return res




def AND(goals, why, proof, top):
    if goals == []:
        return [(copy_proof_tree(proof + [()]), 1.1)]
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

        for (proof1, cf1) in OR(head, why, proof, top):
            for (proof2, cf2) in AND(tail, why, proof1, top):
                res.append((proof2, min(cf1, cf2)))
        return res




def backward(rules, query, *pmode):
    global known, kbase                                # avoid extra args
    kbase = rules
    known = Index().init([(['true'],['true'])]) 
    try:
        for proof in AND(query, [], [(None, (None, {}))], 0):
            topenv = proof[0][1][1]
            report(kbase, topenv, query, pmode, proof[1:])
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




def report(kbase, topenv, query, pmode, how):
    import backward
    try:
        backward.report(kbase, topenv, query, pmode, how)
    except backward.backtrack:
        return
    # else raises stop_proof


