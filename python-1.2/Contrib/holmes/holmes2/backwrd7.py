#
# module backwrd7.py
#
# non-backtracking version of backward.py
# see holmes/backwrk7.py and holmes.doc fore more info;
##############################################################





from match import *
from index import Index
from forward import copy_dict
from backwrd4 import ask_user, report, stop_proof




def OR(goal, why, how, top):
    ask = 1
    res = []
    dict1 = how[top][1][1]

    for rule in kbase.match_then(goal, dict1):
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

    if ask and ask_user(kbase, goal, dict1, known, why):
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


