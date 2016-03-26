#
# RelDB
#
# set processing in python
#
# defines 3 items:
#   class Set  -- basic, generic set processing
#   class RSet -- a Set, with relational algebra
#   test_sets  -- a testing function
#
# a set object (Set): 
# (1) is an unordered collection
# (2) allows heterogeneous collections  
# (3) can grow and shrink arbitrarily
#
# a relational set object (RSet):
# (1) is a Set object
# (2) supports relational algebra operations
#
# users can initialize and concatenate
# sets with normal lists, character strings, 
# tuples (in python), other sets, and other 
# user-defined sequence objects;  users  
# can also use any sequence type (built-in
# or user-defined) on the left-hand side
# of most binary set operations;
#
# sets are unordered collections of arbitrary 
# data items: items can be a mixture of any 
# data type (but some operations assume a
# particular node format);  supports most 
# common set operations, as well as some 
# relational algebra operators (via the Rset
# subclass);
#
# sets are implemented using Python lists (but
# we could use other forms), and encapsulated in 
# a class;  there is a conversion to strings; 
#
# there are many ways to represent relational 
# database tuples and tables in Python:
#   --character strings (and split fields apart)
#   --simple lists ([[name,value], [name,value],...])
#   --Pythin tuples ( (value,value,..) or ((name,value), (name,value),..)
#   --lists with seperate name lists (['f1','f2'..], [a,b,..], [c,d,..])
#   --empty classes (class T:  x = T(); x.f1=a, x.f2=b; ...)
#   --dictionaries ( {'name':value, 'name':value,....}, {...}, .. )
#
# we use dictionaries here for clarity, but they're 
# probably not the most efficient alternative (hashing 
# versus indexing);  each tuple is a dictionary, and
# a table is just a list of dictionaries;  we also don't 
# load tables from an external file-- they are assumed to 
# be already present in the program (dictionary constants 
# in python);  dictionaries are slow to copy and compare
# in python, so they're probably a poor representation
# for tuples/records;
#
# notes:
# 1) Uses python's OOP class facility for sets.  We only
# use inheritance to define the RSet() relational set
# subclass of Set(). Since there's little over-riding of 
# methids in Rset, OOP isn't strictly necessary (we could 
# a module of library functions that operate on simple 
# lists instead).
#
# We could, in priciple, also sub-classes to define 
# different internal formats (list sets, string sets, 
# etc) this would require making the concatenation 
# operation virtual, since '+' needs the same type on 
# each side (different singleton syntax).  Since we 
# use lists internally, we can use the faster '.append'
# list method to concatenate onto a set (versus '+').
#
# 2) Python's 'in' and subscripting are generic, but '+'
# requires the same types on left and right.
# Python's '==' (and therefore 'in') handles lists,
# tuples, dictionaries and strings right (its not
# just address comparison ('is' does that): strings
# compare lexically, lists/tuples are traversed 
# recursively, and dictionaries are compared 
# recursively after their fields are sorted.
#
# 3) We do minimal error checking here: you'll get 
# a normal subscripting or dictionary exception if 
# you do something weird with a set;
#
# 4) example usage:
#    python
#    >>> import sets
#    >>> sets.test_sets()
#
#    >>> from sets import *
#    >>> test_sets()
#    >>> import pbd
#    >>> pdb.run('test_sets()')
#
#    >>> x = Set().init('abd')          (interactive)
#    >>> y = Set().init('db')
#    >>> x.intersect(y)
#
#    >>> from sets import *
#    >>> test_sets()
#    >>> from sets import *
#    >>> table1.join(table2).list([])   (tables exported)
##############################################################  
##############################################################





class Set:



#######################################################
# init() takes an optional argument, and allows the
# init value to be a list, character string, tuple,
# another existing set, or any sequence class object;
#######################################################




    def init(self, *value):
        self.data = []
        if value: 
            self.concat(value[0])
        return self


    def display(self):
        print
        print '<',
        for x in self.data: print x,
        print '>'


    def list(self):
        print
        for x in self.data: print x


    def to_string(self):
        result = ''
        for x in self.data: result = result + x
        return result


    def to_list(self):
        return self.data[:]               # copy list


    def to_RSet(self): 
        return RSet().init(self.data)     # see notes at RSet class




#################################################
# note that self.data can be accessed directly;
# we need copy() since assignment just binds a 
# variable to an existing object: changing one
# variable may effect another variable's value;
#################################################




    def get(self):        
        return self.data    
    

    def set(self, value): 
        self.data = []
        self.concat(value)             # allow any seqence object


    def copy(self):
        return Set().init(self)        # or copy via self.data[:]




 ############################################################
 # insertion, deletion, duplication (in place);
 # concat() allows adding lists, strings, tuples, other 
 # sets, and any other user-defined sequence class object, 
 # to a given set object;
 #
 # concat() uses 'in' to generically iterate over any 
 # sequence type: lists, strings, tuples, and any user-
 # defined sequence class;  any user-defined class
 # which overloads '__len__' and '__getitem__' methods
 # will work with 'in' generation;  our Set class does
 # this too, so 'value' can be another set, and we don't  
 # really need a special type test of the form:
 #      if type(value) == type(self): 
 #           value = value.data
 #
 # notes: 
 # 1) 'x.concat(y.get())' = 'x.concat(y)' = 'x = x + y'
 # 2) 'list.append(x)' is faster than 'list = list + [x]'
 # 3) 'type(self)==type(value)': all class instances 
 #    have the same type, so this only tells us it's an
 #    instance-- we assume its a Set() instance as well;
 #    we need type() since classes can;t over-ride 'in';
 #
 # 4) deletion can be coded many ways in python:
 #     try:
 #         self.data.remove(value)
 #     except: 
 #         pass                      
 #
 #     del self.data[self.data.index(value)]
 #
 #     for i in range(len(self.data)):
 #         if self.data[i] == value
 #             sef.data = self.data[:i] + self.data[i+1:]
 ###########################################################




    def concat(self, value):             
        for x in value:                       # generic iterator   
            self.data.append(x)           
                                              

    def delete(self, value):
        if value in self.data:
            self.data.remove(value)


    def delete_all(self, value):
        while value in self.data:
            self.delete(value)                # Set delete, not list 


    def delete_set(self, sequence):
        for x in sequence:
            self.delete(x)                    # in-place 'difference'

                                      
    def repeat(self, copies):
        self.data = self.data * copies
        



########################################################
# searching (index), function apply and mapping, etc.;
# Pyton has an apply(func,args), but it doesn't 
# apply the funtion to a list;
########################################################




    def search(self, value):              
        for i in range(len(self.data)):     # if value in self.data:  
            if self.data[i] == value:       #    return self.data.index(value)
                return i              
        return -1                     


    def apply(self, func):
        for x in self.data: func(x)


    def map(self, func):
        result = []
        for x in self.data: result.append(func(x))
        return Set().init(result)


    def accum(self, func, start):
        result = start
        for x in self.data: result = func(result, x)
        return result


    def accum_op(self, optr, start):
        result = start
        for x in self.data: result = eval(`result` + optr + `x`)
        return result


    def sum(self):    return self.accum_op('+', 0)

    def prod(self):   return self.accum_op('*', 1)
        
    def abs(self):    return self.map(abs)

    def neg(self):    return self.map(negate)
    
    def square(self): return self.map(square)




##########################################################
# a set member generator;
#
# these routines are mostly superfluous, since we
# can generate set nodes using 'in' in for loops:
#       for x in set:
#           process(x)
#
# we can do this because we've overloaded len() and
# x[i] to work with set instances (see below);  this
# allows 'in' to generate items in a sequence class;
# 
# makes a copy of the set's list (using [:] slices),
# so that generation ignores set changes between next()
# calls (an index/counter can become wrong);
##########################################################




    def first(self):
        self.tail = self.data[:]            
        return self.next()                  
    

    def next(self):
        if self.tail == []:  
            return []
        else:
            head, self.tail = self.tail[0], self.tail[1:]
            return head




############################################
# basic set operations;
# uses very simplistic algorithms;
# also available with operators &, |, ^ ;
#
# note: the right-hand operand to these
# methods ('other') can be another Set,
# or any built-in or user-defined sequence
# type (lists, character strings, tuples.
# other class objects): 'in' generates Set 
# items too;
#
# since 'in' also iterates over the left
# operand ('self'), we don't really need
# to use 'self.data' in the 'if' and 'for'
# statements in the code below (we could
# just use 'self');  but the left must
# be a Set object to call the methods, 
# and using '.data' avoids 1 method call;
############################################




    def intersect(self, other):
        result = []
        for x in self.data:
            if x in other:                     # not 'other.data'
                result.append(x)
        return Set().init(result)


    def union(self, other):
        result = self.data[:]                  # copy list 
        for x in other:
            if not x in self.data:
                result.append(x)
        return Set().init(result)


    def difference(self, other):
        result = []
        for x in self.data:
            if not x in other:
                result.append(x)
        return Set().init(result)
    



################################################################
# set membership, occurrence counts, equivalence, subsumption;
#
# member() and occurs() are not strictly needed:
#
# member -> 
#    'in' works with Set objects, since Set overloads the
#    '__len__' and '__getitem__' methods ('in' works on all
#    sequences generically);  so we can directly code:
#          if value in set:
#               process..
# occurs ->
#    we can simply use the built-in count() list method:  
#          self.data.count(value)
#
# notes:
# 1) 2 sets are 'equivalent' if they have exactly the same 
# elements, but in possibly different orders;
#
# 2) a set 'subsumes' another, if all it contains (at 
# least) all elements in the other set, in any order,
# plus arbitrarily many other items (it must be at least 
# as long as the subsumed set);  this is the same as
# saying the operand is a _subset_ of the object;
###############################################################




    def member(self, value): 
        return (value in self.data)                # boolean 1|0


    def occurs(self, value):
        i = 0
        for x in self.data: 
            if x == value: i = i+1                 # .count     
        return i


    def equiv(self, other):
        copy = other.data[:]                       # dont change other
        for x in self.data:
            if not x in copy:                      # other must be a set
                return 0
            copy.remove(x)
        return (copy == [])


    def subsume(self, other):
        copy = self.data[:]
        for x in other.data:
            if not x in copy:
                return 0
            copy.remove(x)
        return 1




############################################################
# bagof() variants: 
#
# create a new set of items composed of items in the 
# set that satisfy/succeed a given testing function;
#
# bagof() is a generic dispatcher; it selects one  
# of 4 bagof methods based on the datatype of the 
# argument and/or the numberof arguments passed
#
# bagof1() takes a function which must take exactly one
# argument (set item), and return a 0/1 boolean result;
#
# bagof2() takes an arbitrary expression (a string),
# which should evaluate to 0/1 boolean result;  in
# the expression string, the variable name 'x' will
# reference the generated set item (eval() evaluates
# an expression in the context of the eval() call);
#
# bagof3() is bagof2(), except that it creates a
# function enclosing the expression, and passes it
# to bagof() (rather than calling eval() repeatedly)
# (exec() is like eval(), but allows full statements)
#
# bagof4() takes a generation variable, a function,
# and a list of arguments to send the function in the 
# form of a tuple;  it binds the generation variable 
# to successive set items, and calls the function 
# with an argument list composed of members of the
# tuple;  the set item can be referenced by using
# the generation variable in the argument list tuple;
#
# bagof5() is like bagof4(), except that is always 
# places the generated item in argument 1, in the 
# call to the testing funtion; this simplifies the
# interface;
#
# notes:
# 1) 'apply' in bagof4() refers to the built-in apply,
# not the Set method (need self.apply to get to method)
#
# 2) The string expression variants must be used with
# care: you must concatenate the string representation 
# of values into the expr;  this requires backquotes
# for lists and tuple;  since Set overloads __repr__, 
# sets can be printed with backquotes, without having
# to call the '.get()' method to get the set's value list
#
# 3) bagof3() must do eval('_f') to get the function it  
# just created;  using 'global _f' does not seem to avoid
# this: '_f' is likely always stored in the local scope
# when 'def' runs, and the '_f'' refence maps to the global
# scope statically (since its not assigned) ???
#
# 4) bagof4() is a bit tricky...
# Python passes parameters by value (copy)-- this
# really means passing by object reference: the formal
# parameter initially 'shares' the object the actual
# parameter is bound to, but the 2 diverge as soon as
# the formal parameter is reassigned in the function.
#
# But, when the formal/actual share a 'mutable' object,
# changes made to it through the formal will be
# reflected in the actual.  In other words, pass by
# reference can be simulated by using a list object
# enclosing the item, and changing the value of
# the list node.
#
# Also, python has no delayed evaluation, except
# for strings: arguments are fully evaluated in a
# call before the call is made, so use a variable
# in a call that we hope will become successively
# bound insode the function [bagof4(x, member, (x,y))]
#
# For both these reasons, bagof4() requires that  
# the generation variable be passed in as a 1-item
# list, and that the test function expect the 1-item
# list to be passed in;  it rebinds list[0], and
# so changes the value of the generation variable;
############################################################




    def bagof(self, *args):
        if len(args) == 1:
            if type(args[0]) == type(''):
                return self.bagof3(args[0])                # string expr
            else:
                return self.bagof1(args[0])                # 1-arg function
        
        elif len(args) == 2:
            return self.bagof5(args[0], args[1])           # func+extra-args
        elif len(args) == 3:
            return self.bagof4(args[0], args[1]. args[2])  # gen+func+args
        else:
            raise set_error




    def bagof1(self, func):
        res = []
        for x in self.data:
            if func(x): res.append(x)
        return Set().init(res)


    def bagof2(self, expr):
        res = []
        for x in self.data:
            if eval(expr): res.append(x)
        return Set().init(res)


    def bagof3(self, expr):
        exec('def _f(x): return ' + expr + '\n')
        return self.bagof1(eval('_f'))


    def bagof4(self, gen, func, args):
        res = []
        for gen[0] in self.data:
            if apply(func, args): res.append(gen[0])
        return Set().init(res)


    def bagof5(self, func, args):
        res = []
        for x in self.data:
            if apply(func, (x,) + args): res.append(x)
        return Set().init(res)




#
# usage examples
#


    def intersect1(self, other):
        global global_list
        global_list = other
        return self.bagof(in_global_list)
    
    # def in_global_list(x): return x in global_list


    def intersect2(self, other):
        return self.bagof2('(x in ' + `other` + ')')


    def intersect3(self, other):
        return self.bagof3('(x in ' + `other` + ')')
    

    def intersect4(self, other):
        gen = [[]]
        return self.bagof4(gen, member2, (gen, other))

    # def member2(x,y): return (x[0] in y)


    def intersect5(self, other):
        return self.bagof5(member, (other,))

    # def member(x,y): return (x in y)




###################################################################
# sorting;
#
# 3 sorts: 
# sort() does a simple list sort, and uses the builtin method;
# sort_keyed() sorts a list of tuples on a given field's value; 
# sort_keyed2() is like sort_keyed(), but it builds a comparison
# function so it can use the built-in sort() method 
#
# notes: 
# 1) sort_keyed() uses a simple insertion sort (others are better)
# 2) sort_keyed2() must construct a function, since it must 
#    select field values before calling cmp() (and .sort only
#    alows for the 2 operands as parameters)
# 3) Python has a built-in '.reverse()' method for lists;  we
#    write our own for illustration only
# 4) sort() must make an explicit copy of self's list: we can't
#    just code 'copy = self.data', or else we'd wind up sorting
#    'self's list too (.sort is in-place, and '=' just binds)
# 5) sort_keyed2() must backquote the field name (so it gets
#    quoted), and calleval() to fetch the created function (see
#    the bagof() stuff for more setails)
###################################################################




    def sort(self):
        copy = self.copy()             
        copy.data.sort()                            # list sort, not set sort
        return copy


    def sort_keyed(self, field):                    # simple insertion sort
        result = []
        for x in self.data:
            i = 0
            for y in result:
                if x[field] <= y[field]: break
                i = i+1
            result[i:i] = [x]                       # or, result.insert(i,x)
        return Set().init(result)


    def sort_keyed2(self, field):
        func = 'def _cmp(x,y): return cmp(x['+`field`+'], y['+`field`+'])\n'
        exec(func)
        copy = self.copy()
        copy.data.sort(eval('_cmp'))       
        return copy                            # cmp() is builtin: -1,0,+1




#########################################################
# permutations(): generate all permutations of the set
# reversed(): reverse a list manually (not in place)
# subsets(): geneate all subsets of length n
# combos(): generate all combinations of length n
#
# notes: 
# 1) these methods use recursive functions outside
# the class;  the outside functions avoid creating
# new Set objects at each level of the recursion;
#
# 2) subsets() treats '[a,b]' as equivalent to 
# '[b,a]' (and only generates 1 instance); combos()
# treats the 2 cases as different (and gens both--
# order matters); combos() is really just a length
# (size) limited permutations();
#########################################################




    def permutations(self):
        return Set().init(permute(self.data))


    def reversed(self):
        return Set().init(reverse(self.data))


    def subsets(self, n):
        return Set().init(subset(self.data, n))


    def combos(self, n):
        if n > len(self.data):
            return Set().init()
        else:
            return Set().init(combo(self.data, n))




##################################################################
# overload some operators to work with Set instances;
# Python uses special method names to overload operators,
# instead of special syntax (as in C++);
#
# '+' and '*' works for sets as for normal lists, but '+'
# allows appending any sequence type to the set ('+' is not
# generic for built-in types);
#
# notes: 
# 0) it look like difference() and delete_set() are really
# the same (but delete_set( )is done in-place), so '-' and
# '^' are functionally equivalent (oops..);
#
# 1) '+' (and '-' and '*) isn't quite right: 'x = y + value' 
# will also change y;  to be correct, it should make a copy:
#   def __add_(self, value):
#       copy = self.copy()
#       copy.concat(value)
#       return copy
# --> this has now been corrected <-- 
#
# 2) it's critical that we overload __len__ and __getitem__
# (which correspond to len(), and x[i] indexing): this allows 
#
#   (1) 'in' to generate items in the set in 'for' loops, and 
#   (2) 'in' to test membership in conditional expressions
#
# in 'for' loops, 'in' lets us generically iterate over sets 
# just like any other sequence type (lists, strings, tuples,
# other user-defined sequence classes);  this allows us to 
# use just about any sequence type to init or concat onto a
# set, and allows the right-hand-side of a binary set operation
# to be any sequence type;  for example, we can intersect
# a set and a character string:
#
#       x = Set().init(['abcdefg'])
#       x.intersect('aceg')
#
# most binary operations allow non-Set sequence types on the 
# right side, but the left side must be a Set object (or else
# we can't invoke a Set method);
#
# since 'in' also iterates over and test membership in sets, 
# we don't really need to use 'self.data' in the 'if' and 'for'
# statements in most of the code above: we could just use 'self';  
# but, since we know 'self' is a Set (or else we can't call the 
# methods, we can avoid 1 or more method calls by explicitly using 
# the '.data' field name (we avoid calling the __len__ and 
# __getitem__ methods, and instead use the built-in list
# data type's mechanisms (which are presumably faster));
##################################################################




    def __cmp__(self, other): return self.equiv(other)          # ==, <, >
    def __repr__(self):       return `self.data`                # print set
    def __len__(self):        return len(self.data)             # len()
    
    def __getitem__(self, key):    return self.data[key]        # set[i]
    def __setitem__(self, key, x): self.data[key] = x           # set[i]=x
    def __delitem__(self, key):    del self.data[key]           # del set[i]   
    def __getslice__(self, i, j):  return self.data[i:j]        # set[i:j]
    
    def __add__(self, value): 
        res = self.copy(); res.concat(value); return res        #  set + x
    def __sub__(self, value): 
        res = self.copy(); res.delete_set(value); return res    # set - x
    def __mul__(self, value):                 
        res = self.copy(); res.repeat(value); return res        # set * n

    def __or__(self, other):  return self.union(other)          # set | set
    def __and__(self, other): return self.intersect(other)      # set & set
    def __xor__(self, other): return self.difference(other)     # set ^ set

    def __neg__(self): return self.reversed()                   # -set
    def __pos__(self): return self.sort()                       # +set






##################################################
# some utility functions called by the methods
# see descriptions at calling methods;
#
# notes:
# 1) 'member' here is global in the module; it
# does not clash with the 'member' Set method,
# since that function can only be reached via
# qualification (instance.member(), Set.member())
##################################################




set_error = 'Set class error'

def negate(n): return -n
def square(n): return n * n
 
def member(x,y):  return (x in y)
def member2(x,y): return (x[0] in y)               # for intersect4()
def in_global_list(x): return x in global_list     # for intersect1()




def permute(list):
    if list == []:                                  
        return [[]]
    else:
        result = []
        for i in range(len(list)):
            pick = list[i]
            rest = list[:i] + list[i+1:]
            for x in permute(rest):
                result.append([pick] + x)
        return result




def reverse(list): 
    result = []
    for x in list:
        result = [x] + result
    return result                  # or: copy = list; copy.reverse()





# [help], 4 -> [help]
# [help], 3 -> [hel], [hep], [hlp], [elp]
# [help], 2 -> [he], [hl], [hp], [el], [ep] [lp]
# [help], 1 -> [h], [e], [l], [p]



def subset(list, size):
    if size == 0 or list == []:
        return [[]]
    else:
        result = []
        for i in range(0, (len(list) - size) + 1):
            pick = list[i]
            rest = list[i+1:]                            # drop [:i]
            for x in subset(rest, size - 1):
                result.append([pick] + x)
        return result
           



# [help], 4 -> [help], [hepl], [hlep], [hlpe], [hpel], ...
# [help], 3 -> [hel], [hep], [hle], [hlp], [hpe], [hpl], [ehl], ...
# [help], 2 -> [he], [hl], [hp], [eh], [el], [ep], [lh], [le], ...
# [help], 1 -> [h], [e], [l], [p]



def combo(list, size):
    if size == 0 or list == []:                                  
        return [[]]
    else:
        result = []
        for i in range(len(list)):
            pick = list[i]
            rest = list[:i] + list[i+1:]
            for x in combo(rest, size-1):
                result.append([pick] + x)
        return result







##########################################################
##########################################################
# RSet() subclass: basic relational algebra operations;
# assumes items in the set are 'tuples', which 
# are implemented as Python dictionaries (name:value)
#
# implemented as a subclass instance of the general
# class Set(), since these operations require a 
# specific set item format;  note that RSet 
# inherits all Set methods, including its operator
# overloadings;
#
# adds the following methods:
#    select: returns a new set = old where field = value
#    find: like select, but allow general comparison tests
#    match: a generalized select (keys in another set)
#    join: implements normal 'natural' join on a field
#    product: a simple cartesian product operation
#    unique: removes duplicate tuples from a copied set
#    project: normal 'projection' operation
#    copy_tuple: copies a tuple from a table
#    input_tuple: enters tuple fields, and adds to the table
#    input_list: like input, but field names in a list
#    add_tuple: pass in a list/tuple/string of values
#
# over-rides these methods:
#    init
#    list
#    to_string
#
# notes:
# 1) list() allows an optional argument giving the
# names of the fields to be displayed first (any other
# fields of a tuple are given in any order after 
# the fields in the list() argument).  Passing in an
# empty list forces the [name]=value format.
#
# 2) find() could be more general: use bagof()
# directly for arbitrary selection expressions.
# 'or' can sometimes be simulated by using optr
# 'in' with a list of values, but full-blown
# boolean selection exprs must use bagof();
# find() needs backquotes around the field name
# so it's quoted in the resulting expr, as well
# as around the value;
#
# 3) join() and product() must eplicitly copy each
# tuple dictionary: 'copy = dict' just makes copy
# _share_ the object that dict references, and any
# changes in copy change dict too
#
# 4) we compare tuples and test for tuple membership
# in a table using dictionary equality; 'in' works for 
# lists of dictionaries in python: it uses dictionary 
# equality, which sorts the fields, and compares them 
# leixcographically (and compares their values); this 
# is slow, but works (the 'is' operator tests whether
# 2 variables reference the _same_ object);
#
# 5) product() simply concatenates the 2 tuples,
# renaming same-named fields, by appending '_N' to
# duplicae field names (N uniquely identifies the
# field in the resulting tuple);  join() atually
# deletes same-named fields (in the right operand);
#
# 6) input_tuple() and add_tuple() get the field 
# list from an existing tuple in the table, so the
# table can't be empty (and all tuples should have 
# the same fields in any given table (relational));
# input_tuple() and input_list() allow any type 
# value to be entered for a field: it calls eval()
# with the input string, to force the python parser 
# to determine its type by syntax-- users should type
# values using normal pyth syntax ('abd', 123, [..])
#
# 7) These methods return a RSet object, not a Set
# object, so their results can have further rel ops
# applied to them.  In general, Set and RSet objects
# can be mixed: the left operaand must be an RSet to
# invoke the methods, but the left ('other') can be
# a RSet, a normal Set, or any built-in or user-def'd
# sequence object (list, tuple, other class).  Since
# Python is dynamically typed, Sets and RSets can
# be passed to generic routines;  However, we provide 
# a conversion from Set's to RSet's with a simple Set 
# method:
#
#    def to_RSet(self): return RSet().init(self.data)
#
# This is needed if you use a simple Set() method
# which returns a Set, and want to perform RSet
# operations on the result.  There is no good reason
# for a RSet -> Set conversion (RSet's _are_ Set's)
##########################################################
##########################################################





class RSet(Set):


    def init(self, *value):
        if value:
            return Set.init(self, value[0])
        else:
            return Set.init(self)



    def list(self, *first): 
        print 
        print 'table =>'
        for x in self.data:
            if not first:
                print '   tuple =>', x
            else:
                print '   tuple =>',
                for f in first[0]:
                    print '['+f+']=' + `x[f]`,             # backquotes
                for f in x.keys():
                    if not f in first[0]:
                        print '['+f+']=' + `x[f]`,
                print



    def to_string(self):
        raise rset_error, 'cannot convert to a string'

 

    def select(self, field, value):
        result = []
        for x in self.data:
            if x[field] == value:
                result.append(x)
        return RSet().init(result)                  # return RSet, not Set



    def find(self, field, cmp, value):
        return \
            self.bagof('x['+ `field` +'] ' + cmp + ' ' + `value`).to_RSet()



    def match(self, other, field):
        result = []
        for x in self.data:
            for y in other:
                if y[field] == x[field]:
                    result.append(x)
        return RSet().init(result)



    def join(self, other, field):
        result = []
        for x in self.data:
            for y in other:
                if y[field] == x[field]:
                    compos = self.copy_tuple(x)
                    for k in y.keys(): 
                        if not x.has_key(k): 
                            compos[k] = y[k]
                    result.append(compos)
        return RSet().init(result)



    def product(self, other):
        result = []
        for x in self.data:
            for y in other:
                compos = self.copy_tuple(x)
                for k in y.keys(): 
                    if not x.has_key(k): 
                        compos[k] = y[k]
                    else:
                        i = 1
                        while x.has_key(k + '_' + `i`): 
                            i = i+1
                        compos[k + '_' + `i`] = y[k]
                result.append(compos)
        return RSet().init(result)



    def unique(self):
        result = []
        for x in self.data:
            if not x in result:
                result.append(x)
        return RSet().init(result)



    def project(self, fields):
        result = []
        for x in self.data:
            tuple = {}
            for y in fields:
                if x.has_key(y):
                    tuple[y] = x[y]
            if tuple and not tuple in result:
                result.append(tuple)
        return RSet().init(result)



    def copy_tuple(self, tup):
        res = {}
        for field in tup.keys():
            res[field] = tup[field]
        return res



    def input_tuple(self):
        self.input_list(self.data[0].keys())         # use tuple's fields



    def input_list(self, fields):
        tup = {}
        for x in fields:
            valstr = raw_input(x + ' => ')
            tup[x] = eval(valstr)                    # any type: parse it
        self.data.append(tup)



    def add_tuple(self, values):                     # types already known
        tup, i = {}, 0
        if len(values) != len(self.data[0]):
            raise rset_error, 'add_tuple length'
        for x in self.data[0].keys():
            tup[x], i = values[i], i+1
        self.data.append(tup)




rset_error = 'relational set error'







##############################################################
##############################################################
#
# the test driver
#
# notes:
# 1) `['a', 'b']` (backquotes) == '[\'a\', \'b\']'; 
# since find() already backquotes the search value, 
# we don't always need o do it below;
#
# 2) the 'complete', 'available', and 'object' tables
# are computed with relational operators statically;
# we could make these into something like 'schemas'
# if we store them as a string and eval() them to
# get their values on demand;  RSet has no real 
# 'schema' (delayed evaluation) facility as is;
#
# 3) test_sets() exports 6 tables to the global
# scope of the module on exit, so they can be used
# at the interactive propmt.  The user must do 
# another 'from sets import *' _after_ test_sets()
# runs, to get these symbols-- 'import *' statements
# in python get symbols in the module at the time 
# the 'import' executes (it does not get symbols
# added to the module's global scope later on).
# This complexity could be avoided by coding the
# tables global (assign them outside test_sets()).
##############################################################
##############################################################





def test_sets():

    x = Set().init('abcdefg')
    item = x.first()
    while item:                           # generator
        print item,
        item = x.next()
    print

    for item in x: print item,            # 'in' overload
    print

    print ('d' in x ), ('z' in x )        # 'in' overload
    
    x = RSet().init([{'name':'x', 'age':0, 'stats':[1,2,3]}])
    x.list([])
    x.add_tuple(('y', 1, [4,5,6]))
    x.add_tuple(('z', 2, [7,8]))
    x.list([])



    #############################
    # a simple employee database
    #############################


    a = RSet().init( \
            [{'name':'mark',  'job':'engineer'},     \
             {'name':'amrit', 'job':'engineer'},     \
             {'name':'sunil', 'job':'manager'},      \
             {'name':'marc',  'job':'prez'},         \
             {'name':'martin','job':'architect'},    \
             {'name':'jeff',  'job':'engineer'},     \
             {'name':'eve',   'job':'administrator'} \
            ])
    

    b = RSet().init( \
            [{'job':'engineer', 'pay':(25000,60000)},  \
             {'job':'manager',  'pay':(50000,'XXX')},  \
             {'job':'architect','pay':None},           \
             {'job':'prez',     'pay':'see figure 1'}  \
            ])


    c = RSet().init( \
            [{'name':'mark',  'job':'engineer'},     \
             {'name':'amrit', 'job':'engineer'},     \
             {'name':'sunil', 'job':'manager'},      \
             {'name':'john',  'job':'engineer'},     \
             {'name':'steve', 'job':'manager'}       \
            ])


    a.list()
    a.select('job', 'engineer').list()
    a.join(b, 'job').list()
    a.join(b, 'job').list(['name','pay'])

    a.project(['job']).list()      
    a.select('job', 'engineer').project(['name']).list()

    a.find('job', '>', 'engineer').list(['job'])
    c.find('job', '!=', 'engineer').list(['job'])
    a.bagof('x[\'name\'][0] == \'m\'').to_RSet().list(['name'])   
    a.bagof('x[\'job\'] > \'engineer\'').to_RSet().list([])
    a.bagof('x[\'job\'] > \'engineer\' or x[\'name\'] == \'eve\'').\
                                                    to_RSet().list([])

    a.project(['job']).difference(b.project(['job'])).list()
    a.join(b, 'job').project(['name', 'pay']).list()
    a.select('name','sunil').join(b,'job').project(['name', 'pay']).list()
    
    b.product(c).list([])
    a.product(c).list([])
    a.product(c).unique().list([])
    a.product(c).project(['name']).list([])
    a.product(c).project(['name', 'name_1']).list([])

    a.sort_keyed('name').to_RSet().list(['name'])
    a.sort_keyed2('name').to_RSet().list(['name'])
    c.sort_keyed('name').to_RSet().list(['name'])

    a.difference(c).list()
    a.intersect(c).list()
    a.union(c).list()

    print cmp( ((a ^ c) + (a & c)), a) 
    print cmp( ((a ^ c) | (a & c)), a)
    print cmp( ((a ^ c) | c), a)

    print ((a ^ c) + (a & c)).equiv(a) 
    print ((a ^ c) | c).equiv(a)
    print a.difference(c).union(a.intersect(c)).equiv(a)
    


    #########################
    # a languages database
    #########################


    langs = RSet().init([ \
        {'name':'prolog',   'type':'logic',   'rank':5, 'use':'aliens'},  \
        {'name':'alpha',    'type':'proced',  'rank':3, 'use':'glue'},    \
        {'name':'python',   'type':'proced',  'rank':1, 'use':'rad'},     \
        {'name':'icon',     'type':'proced',  'rank':1, 'use':'rad'},     \
        {'name':'scheme',   'type':'funct',   'rank':2, 'use':'aliens'},  \
        {'name':'smalltalk','type':'object',  'rank':4, 'use':'oop'},     \
        {'name':'dylan',    'type':'object',  'rank':7, 'use':'glue'},    \
        {'name':'self',     'type':'object',  'rank':7, 'use':'oop'},     \
        {'name':'rexx',     'type':'proced',  'rank':7, 'use':'shell'},   \
        {'name':'tcl',      'type':'proced',  'rank':6, 'use':'shell'},   \
        {'name':'d',        'type':'unknown', 'rank':7, 'use':'glue'},    \
        {'name':'lisp',     'type':'funct',   'rank':3, 'use':'aliens'},  \
        {'name':'perl',     'type':'proced',  'rank':7, 'use':'shell'}    \
      ])


    course = RSet().init([ \
        {'type':'logic',  'class':'ai'},        \
        {'type':'funct',  'class':'ai'},        \
        {'type':'proced', 'class':'compilers'}, \
        {'type':'logic',  'class':'compilers'}, \
        {'type':'object', 'class':'simulation'} \
      ])


    prof = RSet().init([ \
        {'class': 'ai',       'prof':'travis'}, \
        {'class':'compilers', 'prof':'horwitz'} \
      ])


    dbase     = langs.find('use', 'in', ['glue', 'rad', 'oop'])

    complete  = langs.find('name', 'not in', \
                 ['alpha', 'dylan'])                         # no backquotes
    
    objects   = langs.find('name', 'in', \
                 ['python', 'icon', 'smalltalk', 'self', 'dylan'])
    
    available = langs.find('name', 'not in', \
                 ['dylan', 'self', 'd', 'rexx'])


    dbase.list(['name'])
    langs.join(course,'type').project(['name','class']).list([])
    langs.join(course,'type').join(prof,'class').project(['name','prof']).list()    
    
    langs.select('use','aliens').join(course,'type').project(['class']).list()
    
    for x in ['<', '==', '>']:
        set = langs.find('rank', x, 3)
        set.project(['name', 'rank']).sort_keyed('rank').to_RSet().list([])

    worst = langs.find('rank', '>=', 5)
    worst.sort_keyed('rank').to_RSet().list(['name', 'rank'])

    langs.select('name', 'rad').list([]) 
    langs.select('use',  'rad').list([])
    available.list([])
    objects.list([])

    x = langs.find('use', 'in', ['rad', 'glue'])
    (x & complete & objects & available).to_RSet().project(['name']).list([])
    
    

    #######################
    # miscellaneous tests
    #######################


    print
    x = Set().init('abcdefg')
    print x.intersect('aczeg')
    y = Set().init('aceg')
    print x.intersect(y)

    z1 = Set().init('gcae')
    z2 = z1 + 'x'
    print x.subsume(y), x.subsume(z1), x.subsume(z2)
    print y.equiv(z1),  y.equiv(z2)

    x = Set().init(['h', 'e', 'l', 'p'])
    x.permutations().list()

    for i in range(0, len(x) + 2):                 # 0..5
        x.subsets(i).display()
    for i in range(0, len(x) + 2):
        x.combos(i).display()

    x = Set().init()
    x.set([1,2,3])
    x.permutations().display()

    x = Set().init()
    x.concat('alp')
    print permute(x.get())

    x.concat('po')
    x.display()
    x.reversed().display()
    x.sort().display()
    print x
    print x.to_string()

    print
    x = Set().init([1,2,3,4,5,6])
    y = Set().init([0,2,4,9,6,8,2])
    print x.intersect1(y)
    print x.intersect2(y)
    print x.intersect3(y)          # test bagof generators
    print x.intersect4(y)
    print x.intersect5(y)

    print x.bagof('x in '+`y`)         # dont need y.get()
    print x.bagof(member, (y,))        # dont need y.get()



    ###########################
    # test operator overloads
    ###########################


    print
    x = Set().init('abcd')
    y = Set().init('db')
    print len(x), x + 'efg', x - y, x * 3     # 'x - [..]' uses coerce()
    
    print x[0], x[0:2]
    x[1] = 'z'
    del x[0]
    print x

    print (x == 'abcde'), (x == x)
    print x.equiv(Set().init('abcde')), x.equiv(x)
    
    x.set('abcde')
    y = Set().init('azce')
    z = Set().init('axedy')
    print x | z
    print x & y
    print x ^ z
    print -x + z
    print x & y & z
    print x | y | z
    print x ^ y ^ z     
    print x + y + z
    print x - y - z
    print (x | y - z).display()



    ######################################
    # export tables for interactive tests
    ######################################


    global table1, table2, table2
    table1, table2, table3 = a, b, c

    global langs1, course1, prof1
    langs1, course1, prof1 = langs, course, prof 





#  
# sets.test_sets()
#  
