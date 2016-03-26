#
# module kbase.py
#
# general, administrative routines for knowledge-base processing;
# see holmes/kbase.py and holmes.doc for more info;
####################################################################




from index import Index
from string import *





###################################################################
# rule conversion goes like this:
# string = 'rule x if a ?x, b then c, d ?x' 
# a = ['rule x', 'a ?x, b then c, d ?x']
# b = ['a ?x, b', 'c, d ?x']
# c = ['',' x '] 
# {'rule':'x', 'if':[['a','?x'],['b']], 'then':[['c'],['d','?x']]}
###################################################################




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
           




########################################################
# load and save rules from/to external text files,
# converting them from/to internal format;
#
# change:
# bases now carry indexe with them;  they are triples: 
#     (kbase, if-index, then-index);
#
# change: 
# kbases are now classes (as are indexes);  rules 
# could be classes too (but that would require some 
# extensive code canges);
########################################################




class Kbase:



    def init(self, *file):
        self.rules      = [] 
        self.if_index   = Index().init() 
        self.then_index = Index().init()
        
        if file:
            self.load_rules(file[0])
        return self



    def remove_rule(self, id):                        
        for i in range(len(self.rules)):
            if self.rules[i]['rule'] == id:
                del self.rules[i]
                for if1 in self.rules[i]['if']:
                    self.if_index.delete(if1)
                for then in self.rules[i]['then']:
                    self.then_index.delete(then)



    def add_rule(self, rule):
        self.index_rule(rule)
        self.rules.append(rule)



    def index_rule(self, rule):
        for if1 in rule['if']:
            self.if_index.store(if1, rule)        # fwd: fact/if index tree
        for then in rule['then']:             
            self.then_index.store(then, rule)     # bkwd: goal/then index tree



    def match_if(self, fact):
        return self.if_index.search(fact)



    def match_then(self, goal, dict):
        return self.then_index.search(goal, dict)



    def load_rules(self, name):
        try:
            file = open(strip(name), 'r')
            contents = file.read()                        # 'rule. rule.'
            rules = splitfields(contents, '.')            # ['rule','rule','']
            del rules[len(rules)-1]                       # ['rule','rule']
            for rule in rules:
                self.add_rule(internal_rule(rule))        # [{rule},{rule}]
            file.close()
        except IOError, cause:
            print 'file error:', cause



    def save_rules(self, name):
        try:
            strs = []
            file = open(strip(name), 'w')
            for rule in self.rules:                       # [{rule}, {rule}]
                strs.append(external_rule(rule))          # ['rule.', 'rule.']
            str = joinfields(strs, '\n') + '\n'           # 'rule.\nrule.\n'
            file.write(str)
            file.close()
        except IOError, cause:
            print 'file error:', cause




    ##############################################################
    # the browse method is fairly generic: 
    # (a) with 1 argument (kbase) it dumps the whole kbase; 
    # (b) with 3 arguments (kbase, part, value), it prints 
    #     rules where the selected part is 
    #     (1) equal to the value, or
    #     (2) containing the value, or 
    #     (3) containing an item that contains the value;  
    # (c) with 2 arguments (kbase, value), it applies (b)
    #     to all parts of a rule (parts = 'rule', 'if', 'then')
    ##############################################################




    def browse_pattern(self, string):
        args = ()
        if strip(string) != '':
            for x in internal(string):          # 0, 1 or 2 optional args
                args = args + (x[0],)           # seperated by commas
        apply(self.browse, args)                # run Kbase.browse() method



    def browse(self, *select):
        for rule in self.rules:
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




def islist(x): return (type(x) == type([]))

    
