#
# module index.py
#
# discrimination tree implementation;
# see holmes.doc for a description and example usage;
#
# this module is used by both forward() and backward();
# it manages a single local tree data structure;
#
# change:
# to allow multiple index trees to exist (in forward, 
# we need one for the complete facts list, and one for 
# the new facts deduced at each step), this is now 
# a class, rather than a simple module;  this is slightly
# less convenient, since we need to pass indexes around;
#
# note:
# it appears that using slices [1:] to traverse list
# cdr's in recursion is slightly faster than using
# indexing, and passing indexes in recursion, even though
# the slice copies the sublist block;
#
# note: 
# the fact that python shares, rather than copies, object
# references comes in very handy here: when we index 
# rules, we store the rule redundantly at the leaves of
# the index trees-- we really only store a reference
# (pointer) to the rules, not copies of their dictionary
# representation;
#############################################################




from match import ground, substitute




class Index:

    

    def init(self, *items):
        self.tree = {'.':[]}                                # empty tree
        if items:                                           # '.' empty pattern
            for (key, val) in items[0]:
                self.store(key, val)
        return self




    def store(self, pattern, item):
        level = self.tree
        for sym in pattern:
            if sym[0] != '?':
                if not level.has_key(sym):                  # store const
                    level[sym] = {'.':[]}                   # no items yet
                level = level[sym]
            else:
                if not level.has_key('?'):                  # store var
                    level['?'] = {'.':[]}                   # alt: [[],{}]
                level = level['?']
        level['.'].append(item)                             # add at level[n]




    def matches(self, pattern, level, dict):                # ['.'] may = []
        if pattern == []:                                   # may be too long
            return level['.']                               # may be too short
        else:                                               # may not match
            res = []
            head, tail = pattern[0], pattern[1:]
            if dict:
                head = ground(head, dict[0])[0]

            if head[0] != '?':                         
                if level.has_key(head):
                    res = res + self.matches(tail, level[head], dict)
                if level.has_key('?'):
                    res = res + self.matches(tail, level['?'], dict)
            else:
                for x in level.keys():
                    if x != '.':
                        res = res + self.matches(tail, level[x], dict)
            return res




    def search(self, pattern, *dict): 
        toplevel = self.tree                      
        return self.matches(pattern, toplevel, dict)            # recursive
                                                           



    def delete(self, pattern):
        level = self.tree
        for sym in pattern:
            if sym[0] == '?':
                if not level.has_key('?'):
                    return 
                level = level['?']
            else:
                if not level.has_key(sym):
                    return
                level = level[sym]
        level['.'] = []




    def search_unique(self, pattern):
        level = self.tree
        for sym in pattern:
            if sym[0] == '?':
                if not level.has_key('?'):
                    return []
                level = level['?']
            else:
                if not level.has_key(sym):
                    return []
                level = level[sym]
        return level['.']




    def store_unique(self, pattern, item, *dict):
        level  = self.tree
        for sym in pattern:
            if dict:
                term = ground(sym, dict[0])[0]
            else:
                term = sym

            if term != '?':
                if not level.has_key(term):                 # store const
                    level[term] = {'.':[]}                  # no items yet
                level = level[term]
            else:
                if not level.has_key('?'):                  # store var
                    level['?'] = {'.':[]}
                level = level['?']
        
        if level['.'] != []:
            return 0
        else:
            if dict:
                level['.'] = [substitute(item, dict[0])]
            else:
                level['.'] = [item]
            return 1




    def generate(self, level):
        res = []
        for key in level.keys():
            if key != '.':
                res = res + self.generate(level[key])
        return res + level['.']

    def members(self):
        return self.generate(self.tree)         # collect data at leaves




    def trace(self, level, keys):
        for key in level.keys():
            if key != '.':
                self.trace(level[key], keys+[key])
        print keys, '->', level['.']

    def display(self):
        self.trace(self.tree, [])               # print all keys/data

