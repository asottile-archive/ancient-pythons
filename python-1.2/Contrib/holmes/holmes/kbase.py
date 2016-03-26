#
# module kbase.py
#
# general, administrative routines  
# for knowledge-base processing;
# see holmes.doc for descriptions;
# exports everything here;
#####################################



from string import *



def external(conjunct):                         # [[a,b],[c,d]] -> 'a b, c d'
    strs = []
    for clause in conjunct:
        strs.append(join(clause))               # -> ['a b', 'c d']    
    return joinfields(strs, ', ')               # -> 'a b, c d'



def internal(conjunct):                         # 'a b, c d' -> [[a,b],[c,d]]
    res = []                                    
    for clause in splitfields(conjunct, ','):   # -> ['a b', ' c d']    
        res.append(split(clause))               # -> [['a','b'],['c','d']]
    return res





###################################################################
# rule conversion goes like this:
# string = 'rule x if a ?x, b then c, d ?x' 
# a = ['rule x', 'a ?x, b then c, d ?x']
# b = ['a ?x, b', 'c, d ?x']
# c = ['',' x '] 
# {'rule':'x', 'if':[['a','?x'],['b']], 'then':[['c'],['d','?x']]}
###################################################################




def internal_rule(string):              
    a = splitfields(string, ' if ')         
    b = splitfields(a[1], ' then ')        
    c = splitfields(a[0], 'rule ')        
    return {'rule':strip(c[1]), 'if':internal(b[0]), 'then':internal(b[1])}



def external_rule(rule):
    return 'rule '    + rule['rule']           + \
           ' if '     + external(rule['if'])   + \
           ' then '   + external(rule['then']) + '.'



def print_fact(f): print external([f])
def print_rule(r): print external_rule(r)



def remove_rule(kbase, id):                        
    for i in range(len(kbase)):                 # for interactive use
        if kbase[i]['rule'] == id:
            del kbase[i]




########################################################
# load and save rules from/to external text files,
# converting them from/to internal format;
#
# uses 'split', 'splitfields', etc. to load the rules;
# in retrospect, we could have done without the '.'
# at the end of rules (since they're seperated by 
# 'rule' already), and should really have parsed the
# kbase file explicitly, so errors could be detected
# and reported [here, we just make garbage if ',' or '.'
# missing or redundant; a good test is '!- len(kbase)'
# in the shell to see if all rules loaded ok];
#
# the method here illustrates a rapid-prototyping 
# approach (parsing is essentially the same in all
# languages, and so is not a good benchmark);
#
# note: 'if' and 'then' can appear in a rule's patterns,
# but not ' if ' or ' then ';
#
# note: rules can be spread across > 1 line, and > 1
# rule can appear on any line;  we load the entire file
# into a string (.read): it will contain '\n' at 
# arbitrary places, but these get removed by split()
# and strip(), which are called be internal_rule()
# blank lines can appear between rules arbitrarily;
########################################################




def load_rules(name):
    kbase = []
    try:
        file = open(strip(name), 'r')
        contents = file.read()                          # 'rule. rule.'
        rules = splitfields(contents, '.')              # ['rule','rule','']
        del rules[len(rules)-1]                         # ['rule','rule']
        for rule in rules:
            kbase.append(internal_rule(rule))           # [{rule},{rule}]
        file.close()

    except IOError, cause:
        print 'file error:', cause
    return kbase




def save_rules(kbase, name):
    try:
        strs = []
        file = open(strip(name), 'w')
        for rule in kbase:                              # [{rule}, {rule}]
            strs.append(external_rule(rule))            # ['rule.', 'rule.']
        str = joinfields(strs, '\n') + '\n'             # 'rule.\nrule.\n'
        file.write(str)
        file.close()

    except IOError, cause:
        print 'file error:', cause




##############################################################
# this routine is fairly generic: 
#
# (a) with 1 argument (kbase) it dumps the whole kbase; 
# (b) with 3 arguments (kbase, part, value), it prints 
#     rules where the selected part is 
#     (1) equal to the value, or
#     (2) containing the value, or 
#     (3) containing an item that contains the value;  
# (c) with 2 arguments (kbase, value), it applies (b)
#     to all parts of a rule (parts = 'rule', 'if', 'then')
#
# for example, if part = 'if', and value = 'man', it will 
# print all rules that mention 'man' anywhere in their 'if' 
# conjunctions;  if 'part' is not passed, it prints all rules
# mentioning 'man' in their 'if', 'then', or 'rule' parts.
# if value = a clause (a list), yo can select rules with 
# a specific clause in their if and/or then parts
##############################################################




def islist(x): 
    return (type(x) == type([]))




def browse(kbase, *select):
    for rule in kbase:
        if not select:
            print_rule(rule)

        else:
            if len(select) == 2:
                parts, value = (select[0],), select[1]
            else:
                parts, value = ('rule', 'if', 'then'), select[0]
  
            for part in parts:
                if rule[part] == value:
                    print_rule(rule)
                else:
                    if islist(rule[part]):
                        if value in rule[part]:
                            print_rule(rule)
                        else:
                            for x in rule[part]:
                                if islist(x) and value in x:
                                    print_rule(rule)




def browse_pattern(kbase, string):
    args = (kbase,)
    if strip(string) != '':
        for x in internal(string):          # 0, 1 or 2 optional args
            args = args + (x[0],)           # seperated by commas
    apply(browse, args)                     # run kbase.py browse()

    
