#
# module forward2.py
#
# forward chaining inference engine
#
# this is a varient of forward.py that implements
# negation both by explicit assertion, and by
# ommission;  see holmes.doc for more info;
# to use negation-by-ommission in the shell:
#       holmes> +2
# to use it in a program, just import forward2;
###########################################################################

                              


import forward; forward1 = forward

from match import *
from forward import copy_dict, ask_user




def forward(kbase, facts, *pmode):
    temp = forward1.conjunct
    forward1.conjunct = conjunct                     # over-ride 1 function
    res = forward1.forward(kbase, facts, pmode)      # call forward.py version
    forward1.conjunct = temp
    return res




#################################################
# generate bindings for rule's 'if' conjunction: 
# find intersected bindings at this 'AND' node,
# and construct proof subtree lists as the
# recursion unfolds with valid solutions;
#################################################




def conjunct(ifs, known, dict, why):
    if ifs == []:
        return [(copy_dict(dict), [])]                # all conjuncts matched
    
    res = []
    head, tail = ifs[0], ifs[1:]
    if head[0] == 'ask':
        term = substitute(head[1:], dict)
        if ask_user(term, known, why):
            for (dict2, proof2) in conjunct(tail, known, dict, why):
                res.append((dict2, [(term, 'told')] + proof2))


    elif head[0] == 'not':
        term = substitute(head[1:], dict)
        if not known.search_unique(term) or \
           known.search_unique(['not'] + term):  
            for (dict2, proof2) in conjunct(tail, known, dict, why):
                res.append((dict2, [(term, 'not')] + proof2))


    else:
        for (fact, proof) in known.search(head, dict): 
            matched, changes = match(head, fact, dict, {})
            if matched:
                for (dict2, proof2) in conjunct(tail, known, dict, why):
                    res.append((dict2, [(fact, proof)] + proof2))
            for (var, env) in changes:
                env[var] = '?'                        
    return res

