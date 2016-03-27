#
#          R O M A N   N U M E R A L S   (python version)
#
#  This program takes Arabic numerals from standard input and writes
#  the corresponding Roman numerals to standard outout.



##########################################################################
# the icon version:
#
# procedure main()
#    local n
#    while n := read() do
#       write(roman(n) | "cannot convert")
# end
# 
# procedure roman(n)
#    local arabic, result
#    static equiv
#    initial equiv := ["","I","II","III","IV","V","VI","VII","VIII","IX"]
#    integer(n) > 0 | fail
#    result := ""
#    every arabic := !n do
#       result := map(result,"IVXLCDM","XLCDM**") || equiv[arabic+1]
#    if find("*",result) then fail else return result
# end
#
##########################################################################



import sys
from string import *            # atoi unqualified



# 
# the main driver
#


def romans(converter):
    while 1:
        roman = converter(raw_input('enter number: '))
        if roman != None: 
            print roman
        else: 
            print 'cannot convert'




#
# simplest approach: implement map() inline;
# note: 'equiv' could be global in the module for 'static'
#



def roman1(n):
   equiv = ['','I','II','III','IV','V','VI','VII','VIII','IX']        
   if atoi(n) <= 0: return None
   result = ''
   for arabic in n:
       new = ''
       key, to = 'IVXLCDM*', 'XLCDM***'       # extra '*' or index fails
       for x in result:
           new = new + to[index(key, x)]
       result = new + equiv[atoi(arabic)]     # atoi needed here
   if '*' in result: return None
   return result




#
# use a dictionary for mapping
#



def roman2(n):
    
    dig = {'0':'',  '1':'I',  '2':'II',  '3':'III',  '4':'IV', \
           '5':'V', '6':'VI', '7':'VII', '8':'VIII', '9':'IX'}  
           
    map = {'I':'X', 'V':'L', 'X':'C', \
           'L':'D', 'C':'M', 'D':'*', 'M':'*', '*':'*'}                    
    
    if atoi(n) <= 0: return None
    result = ''
    for arabic in n:
        new = ''; 
        for x in result: new = new + map[x]
        result = new + dig[arabic]
    if '*' in result: return None
    return result




#
# make our own map();  could add to string.py;
# note: this is the best comparison to the icon version;
# note: can't change strings directly in python;
#



def map(string, key, to):
    result = ''
    for x in string:
        result = result + to[index(key, x)]
    return result


def roman3(n):
    dig = ['','I','II','III','IV','V','VI','VII','VIII','IX']        
    if atoi(n) <= 0: return None
    result = ''
    for arabic in n:
        result = map(result, 'IVXLCDM*', 'XLCDM***') + dig[atoi(arabic)]
    if '*' in result: return None
    return result




#
# alternative ways to map(): slices and (of course) recursion
#



def map2(string, key, to):
    result = string
    for i in range(len(string)):
        result = result[:i] + to[index(key,string[i])] + result[i+1:]
    return result



def map3(string, key, to):
    if string == '':
        return ''
    else:
        return to[index(key, string[0])] + map3(string[1:], key, to)




#
# do the lisp thing: convert strings<->lists for mapping
#



def explode(string):
    list = []
    for x in string: list.append(x)
    return list

def implode(list):
    string = ''
    for x in list: string = string + x
    return string


def tuple_implode(list):
    tuple = ()
    for x in list: tuple = tuple + (x,)
    return tuple

def tuple_explode(tuple): return explode(tuple)





#####################################################
# generic sequence conversion, via function pointers;  
# 3 cases suffice for all sequence conversion cases;
#
# ie, only target sequence type matters, since 'in'
# can iterate through any of the 3 types generically
# but need different start/singleton constructors;
#
# note: can't use 'in' or '+' with dictionaries;
#####################################################



def seqcon1(source, start, single):
    result = start
    for x in source: result = result + single(x)
    return result


def explode2(string):      seqcon1(string, [], list)   # string->list 
def tuple_explode2(tuple): explode2(tuple)             # tuple->list 
def implode2(list):        seqcon1(list, '', string)   # list->string
def tuple_implode2(tuple): implode2(tuple)             # tuple->string 
def list_tuple(list):      seqcon1(list, (), tuple)    # list->tuple
def string_tuple(string):  list_tuple(string)          # string->tuple


def list(x):   return [x]
def string(x): return x
def tuple(x):  return (x,)







#################################################
# generic, using target switch logic or tables
#################################################



def seqcon2(source, target):
    starts = ['', [], ()]
    single = [string, list, tuple]
    result = target
    for x in source: result = result + single[starts.index(target)](x)
    return result


def seqcon3(source, target):
    config = {'string':('',string), 'list':([],list), 'tuple':((),tuple)}
    result = config[target][0]
    for x in source: result = result + config[target][1](x)
    return result


def seqcon4(source, target):
    result = target
    for x in source: 
        if   target == '': result = result + x
        elif target == []: result = result + [x]
        elif target == (): result = result + (x,)
    return result


def seqcon5(source, target):
    config = {'string':('','x'), 'list':([],'[x]'), 'tuple':((),'(x,)')}
    result = config[target][0]
    for x in source: result = result + eval(config[target][1])
    return result


def seqcon6(source, target):
    start, single = \
        {'string':('','x'), 'list':([],'[x]'), 'tuple':((),'(x,)')}[target]
    result = start
    for x in source: result = result + eval(single)
    return result





########################################################
# or use a generic sequence class;
#
# manages a sequence data object internally, and
# keeps track of its actual type manually;
#
# note: methods calls require '()', so data member refs
# don't look same as function member calls (without 
# the '()', function members are accessed directly;
#
# note: the .value() method is really superfluous,
# since the value can be accessed directly using
# the .data member;  get/set function members
# are useful iff the data interface may have to
# be made functional later, or you want to set
# the value with a function call [x=Obj().set(val)]
#   def set(self, val): self.data = val
#
# expected output:
#   >>> test_sequence()
#   abcde
#   ['a', 'b', 'c', 'd', 'e']
#   zbcde
#   []
#   ['a', 'b']
#   ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
#   ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i')
#   ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k')
#   abcdefghijk
#   abcdefghijkl
#   ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
#   a
#   b
#   ...
#   k
#   l
########################################################





class Sequence:
    def to_string(self):
        res = ''
        for x in self.data: res = res + x
        self.data = res
    
    def to_list(self):
        res = []
        for x in self.data: res.append(x)
        self.data = res
    
    def to_tuple(self):
        res = ()
        for x in self.data: res = res + (x,)
        self.data = res

    def add(self, item):
        if   type(self.data) == type(''): single = item
        elif type(self.data) == type([]): single = [item]
        elif type(self.data) == type(()): single = (item,)
        self.data = self.data + single

    def concat(self, items):
        for x in items: self.add(x)         # 'in' is generic

    def value(self): return self.data

    def init(self, *value):  
        if value == ():
            self.data = []                  # starts as a list
        else:    
            self.data = value[0]            # opt value gives start type
        return self

    def show(self):  
        for x in self.data: print x         # indent needed here




def test_sequence():
    l = Sequence().init('')
    l.concat('abcde')
    print l.value()

    l.to_list()         # explode
    print l.value()

    l.data[0] = 'z'
    l.to_string()       # implode
    print l.value()

    x = Sequence().init()
    print x.value() 
    
    x.add('a'); x.add('b') 
    print x.value()   
    
    x.concat('cd');
    x.concat(['e', 'f'])                    # '+' needs same types
    x.concat(('g', 'h', 'i'))
    print x.value() 

    x.to_tuple();     print x.data  
    x.concat('jk');   print x.data  

    x.to_string();    print x.data  
    x.concat(['l']);  print x.data 

    x.to_list();      print x.data  
    x.show();





###############################################################
# use specialization/inheritance;
#
# object type implies single/inits;
# build a new object type to convert 
# types (and reset virtual funcs);
#
# this could be used for a Sequence2:
#    def init(self): return List().init()
# to try and default to a List when 
# a Sequence() is made; we cant' use it 
# here because init() is more complex;
# 
# same expected output as test_sequence()
###############################################################





class Sequence2:
    def convert(self, maker):
        new = maker().init() 
        new.concat(self.data)
        return new

    def to_string(self): 
        return self.convert(String)        # classes are 1st-class    

    def to_list(self):   
        return self.convert(List)
    
    def to_tuple(self):  
        return self.convert(Tuple)
    
    def concat(self, items):                # "in" is generic
        for x in items: self.add(x)         # add is virtual
    
    def init(self, *value):                 # optional value arg
        if not value:                       # '()' is false
            self.data = self.empty()        # empty is virtual
        else:
            self.data = value[0]
        return self
    
    def show(self): 
        for x in self.data: print x




class List(Sequence2):
    def empty(self): 
        return []  

    def add(self, item): 
        self.data.append(item)                   # faster than '+ [item]'


class String(Sequence2):
    def empty(self):
        return ''

    def add(self, item): 
        self.data = self.data + item
 

class Tuple(Sequence2):
    def empty(self):
        return ()

    def add(self, item): 
        self.data = self.data + (item,)




def test_sequence2():
    l = String().init()
    l.concat('abcde')
    print l.data

    l = l.to_list()     # explode
    print l.data

    l.data[0] = 'z'
    l = l.to_string()   # implode
    print l.data


    x = List().init()                  # start as a list
    print x.data                       # drop value() method 
    
    x.add('a'); x.add('b') 
    print x.data   
    
    x.concat('cd');
    x.concat(['e', 'f'])               # '+' needs same types
    x.concat(('g', 'h', 'i'))
    print x.data 

    x = x.to_tuple();  print x.data    # must assign new obj  
    x.concat('jk');    print x.data  

    x = x.to_string(); print x.data  
    x.concat(['l']);   print x.data 

    x = x.to_list();   print x.data  
    x.show();






#############################################
# ok: finally, mapping via explode/implode
#############################################



def map4(string, key, to):
    list = []
    for x in string:
        list.append(to[index(key, x)])
    return implode(list)


def map5(string, key, to):
    list = explode(string)
    for i in range(len(list)):
        list[i] = to[index(key, list[i])]
    return implode(list)


def map6(string, key, to):
    list = explode(string); i = 0
    for x in list:
        list[i] = to[index(key, x)]; i = i+1
    return implode(list)


# does not work: x doesn't "share" with nodes in list
#
# def map7(string, key, to):
#    list = explode(string)
#    for x in list:
#        x = to[index(key, x)]
#    return implode(list)





########################################
# a few more coding variations..
########################################



def roman4(arab):
   equiv = ['','I','II','III','IV','V','VI','VII','VIII','IX']        
   if atoi(arab) <= 0: return None
   res = ''
   while arab != '':
       new, key, to = '', 'IVXLCDM*', 'XLCDM***'
       while res != '':
           new, res = new + to[index(key, res[0])], res[1:]
       res, arab = new + equiv[atoi(arab[0])], arab[1:]
   if '*' in res: return None
   return res





##############################################################
# note: illegal to ref undefined names: must 
# explicitly initialize res and new to '' here;
#
# note: this is illegal syntax (cmp stmts require indent):
#   res=''; while arab != '':
#       new=''; while res != '':
#           new, res = ...
#
# ok to subscript literals, but some methods useless:
#   [1,2,3].index(3) ok (2)
#   [1,2,3].append(5) means nothing (append returns no value)
#   'abcd'[1] ok ('b')
#   'abcd'.rjust(3) fails
#   string.rjust('abcd',3) ok (strings not really a class)
#   {'a':1, 'b':2}['a'] ok (1)
############################################################## 




def roman5(arab):
   equiv = ['','I','II','III','IV','V','VI','VII','VIII','IX']        
   if atoi(arab) <= 0: return None
   res = ''; 
   while arab != '':
       new = ''; 
       while res != '':
            new, res = new + 'XLCDM***'[index('IVXLCDM*',res[0])], res[1:]
       res, arab = new + equiv[atoi(arab[0])], arab[1:]
   if '*' in res: return None
   return res






#######################################################
# test all varients: functions are 1st-class objects;
# can test others by hand at interactive prompt:
#   >>> from roman import *
#   >>> seqcon(...
#
#   >>> import roman
#   >>> roman.seqcon(...
#
#   >>> import pdb
#   >>> pdb.run('from roman import *')
#   >>> pdb.run('test_sequence2()')
#
# this code gets run when the module roman.py is 
# imported (loaded);  it must be after the def's
# above, since funcs aren't known till def runs;
#######################################################




def doit():
    roman_funcs = [roman1, roman2, roman3, roman4, roman5]
    for x in roman_funcs:
        print '--running function:', roman_funcs.index(x) + 1
        try: 
            romans(x)
        except:
            print sys.exc_type + ':', sys.exc_value
    


doit()


