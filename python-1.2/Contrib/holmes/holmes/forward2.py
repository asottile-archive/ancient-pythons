#
# module forward2.py
#
# forward chaining inference engine;
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
from forward import copy_dict, ask_user, asserted




def forward(kbase, facts, *pmode):
    temp = forward1.bindings
    forward1.bindings = bindings                     # over-ride 1 function
    res = forward1.forward(kbase, facts, pmode)      # call forward.py version
    forward1.bindings = temp
    return res




#################################################
# generate bindings for rule's 'if' conjunction: 
# find intersected bindings at this 'AND' node,
# and construct proof subtree lists as the
# recursion unfolds with valid solutions;
#
# note: this function executes with global 
# scope = module forward2.py, but the rest of
# the system executes with global scope =
# module forward.py;
#
# note: this isn't exactly like forward.py
# for explicitly asserted 'not' facts, since
# we don't carry variable bindings from the
# match (we do a simple ground comparison);
#################################################




def bindings(ifs, facts, dict, why):
    if ifs == []:
        return [(copy_dict(dict), [])]                # all conjuncts matched
    
    res = []
    head, tail = ifs[0], ifs[1:]
    if head[0] == 'ask':
        ground = substitute(head[1:], dict)
        if ask_user(ground, facts, why):
            for (dict2, proof2) in bindings(tail, facts, dict, why):
                res.append((dict2, [(ground, 'told')] + proof2))

    elif head[0] == 'not':
        ground = substitute(head[1:], dict)
        if not asserted(ground, facts) or asserted(['not']+ground, facts):  
            for (dict2, proof2) in bindings(tail, facts, dict, why):
                res.append((dict2, [(ground, 'not')] + proof2))
         
    else:
        for (fact, proof) in facts: 
            matched, changes = match(head, fact, dict, {})
            if matched:
                for (dict2, proof2) in bindings(tail, facts, dict, why):
                    res.append((dict2, [(fact, proof)] + proof2))
            for (var, env) in changes:
                env[var] = '?'                        
    return res

