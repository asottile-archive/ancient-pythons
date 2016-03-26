#
# module forward.py
#
# forward chaining inference engine
# see holmes.doc for description
# exports forward(kbase, facts)
#
# forward(kbase, facts)     -> prints all facts deduced
# forward(kbase, <filter>)  -> prints all deduced facts matching <filter>
# forward(kbase, None)      -> returns the list of deduced facts
###########################################################################




from match import *
from kbase import external, internal, browse_pattern
from time import time

stop_chaining = 'stop_chaining'




def forward(kbase, facts, *pmode):
    time1 = time()
    global rulebase                             # avoid extra args
    rulebase = kbase
    known = []
    for x in facts:
        known.append((x, 'initial'))            # fact, reason/proof
    known.append((['true'], 'atomic'))          # if true then f1, f2,..
    
    try:
        chain(kbase, known)                     # adds to 'known'
    except stop_chaining: pass                  # user can stop it
    return report(known, pmode, time1)
    



def chain(kbase, facts):
    global user_answers                         # avoid extra args
    while 1:
        user_answers = 0
        rules = satisfied(kbase, facts)         # 'if' parts matched
        if not rules and not user_answers:
            break                               # no rules matched
        deduced = fire(rules, facts)            # add 'then' to facts
        if not deduced and not user_answers:
            break                               # no new facts added
                                                # ask_user added no facts



#################################################
# add 'then' parts of matched rules/bindings
#################################################




def fire(solns, known):
    added = 0
    for (rule, dict, proof) in solns:
        for then in rule['then']:
            fact = substitute(then, dict)
            if fact[0] == 'delete': 
                for (kfact, kproof) in known: 
                    if fact[1:] == kfact: 
                        known.remove((kfact, kproof))
            else:
                for (kfact, kproof) in known:
                    if fact == kfact: break
                else:
                    added = 1
                    known.append((fact, (rule['rule'], proof))) 
    return added




#############################################
# pick rules with matched 'if' parts
#############################################




def satisfied(kbase, facts):
    solns = []
    for rule in kbase:
        for (dict, proof) in bindings(rule['if'], facts, {}, rule['rule']):
            solns.append((rule, dict, proof))
    return solns




#####################################################
# generate bindings for rule's 'if' conjunction: 
# find intersected bindings at this 'AND' node,
# and construct proof subtree lists as the
# recursion unfolds with valid solutions;
#
# note: takes less code to append to proof 
# before recursive call, but may make more 
# list copies (since path may not succeed);
#
# note: 'not' goals must match explicitly asserted
# 'not' facts: we just match the whole 'not';
#####################################################




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
    
    else:
        for (fact, proof) in facts: 
            matched, changes = match(head, fact, dict, {})
            if matched:
                for (dict2, proof2) in bindings(tail, facts, dict, why):
                    res.append((dict2, [(fact, proof)] + proof2))
            for (var, env) in changes:
                env[var] = '?'                        
    return res




########################################################
# assorted stuff; dictionary copies should be built-in,
# since dictionary assignment 'shares' the same object; 
########################################################




def copy_dict(dict):
    res = {}
    for f in dict.keys(): res[f] = dict[f]
    return res
        



def asserted(fact, known):
    for (fact1, proof) in known:
        if fact1 == fact: return 1       # list equality
    return 0




##########################################################
# the 'why' explanation in forward chaining just lists
# the rule containing the asked goal;  since the proof
# tree is just 2-levels deep, there is no stack of
# currently active goals to trace;  users can also
# check o progress so far ('where'), and stop the 
# chaining in its current state and report ('stop');
##########################################################




def ask_user(fact, known, why):
    global user_answers
    for (item, proof) in known:
        if item == fact: 
            return 1
        if item == ['not'] + fact: 
            return 0

    user_answers = 1
    while 1:
        ans = raw_input('is this true: ' + external([fact]) + ' ?') 
        if ans in ['y','Y','yes','YES']:
            known.append((fact, 'told'))
            return 1
        elif ans in ['n','N','no','NO']:
            known.append((['not'] + fact), 'told')
            return 0
        elif ans == 'why':
            print 'to see if rule', why, 'can be applied'
        elif ans == 'where':
            print_solns(known, None)
        elif ans == 'browse':
            browse_pattern(rulebase, raw_input('enter browse pattern: '))
        elif ans == 'stop':
            raise stop_chaining
        else:
            print 'what? ',
            print '(expecting "y", "n", "why", "where", "browse", or "stop")'




######################################################
# 'how' explanations require us to construct proof 
# trees for each fact added to the known facts list; 
# to do this, we concatenate the sub-proof tree for 
# each 'if' conjunct onto a list, for each fired rule;  
# since the conjuncts are matched to already known 
# facts, the new proof trees inherit their fact's 
# trees: ie, we construct each fact's proof tree 
# bottom-up, sing the trees associated with already
# deduced facts used to fire a rule;  this isn't too 
# expensive, since object ref's always share (not 
# copy) the ref'd object (sub-proof tree, dict, etc.)
######################################################




def report(facts, pmode, time1):
    filter = None
    if pmode:
        if pmode[0] == None:
            return facts
        else:
            filter = pmode[0]
    time2 = time() - time1
    print_solns(facts, filter)
    print 'time: ', time2
    show_proofs(facts)




def print_solns(facts, filter):
    sources = {'rule':[], 'told':[], 'init':[], 'atom':[]}

    for (fact, proof) in facts:
        if not filter or match(filter, fact, {}, {})[0]:
            if type(proof) == type(()):
                sources['rule'].append((fact, proof))         # deduced
            elif proof == 'told' or proof == 'not':
                sources['told'].append(fact)        
            elif proof == 'initial':
                sources['init'].append(fact)        
            elif proof == 'atomic':
                sources['atom'].append(fact)
    
    if not sources['rule']:
        print 'I have not deduced any new facts.'
    else:
        print 'I deduced these facts...'
        for (fact, proof) in sources['rule']:
            print '  ', external([fact])        #, '(by rule', proof[0] + ')'

    if sources['told']:
        print 'You told me these facts...'
        for fact in sources['told']: 
            print '  ', external([fact])

    if sources['init']:
        print 'I started with these facts...'
        for fact in sources['init']: 
            print '  ', external([fact])

    # ignore sources['atom']
   


                                                  
#######################################################
# know facts list records proof trees of the form:
#
#      [ (fact, 'told'),
#        (fact, (rule-id, 
#                  [(fact, proof), (fact, proof), ..]
#        (fact, proof), ...
#      ]
#
# we get one such node here;  all facts are fully 
# grounded/evaluated on known list;
#######################################################
    



def show_proofs(known):
    while 1:
        print
        ans = raw_input('show proofs? ')
        if ans in ['y','Y','yes','YES']:
            [patt] = internal(raw_input('enter deductions pattern: '))
            for (fact, proof) in known:
                if match(patt, fact, {}, {})[0]:
                    trace_tree((fact, proof), 0)
        elif ans in ['n','N','no','NO']:
            break
        elif ans == 'where':
            print_solns(known, None)
        elif ans == 'browse':
            browse_pattern(rulebase, raw_input('enter browse pattern: '))
        else:
            print 'what?  (expecting "y", "n", "where", or "browse")'




def trace_tree((fact, proof), level):
    print ' ' * level,
    print '"' + external([fact]) + '"', 
    if proof == 'told':
        print 'was your answer'
    elif proof == 'initial':
        print 'was on your initial facts list'
    elif proof == 'atomic':
        print 'is an absolute truth'
    elif proof == 'not':
        print 'was a negative answer, or was ommitted'
    else:
        rule, subproof = proof
        print 'was deduced by firing rule', rule
        for branch in subproof:
            trace_tree(branch, level+3)

