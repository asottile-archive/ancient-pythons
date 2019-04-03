# Module 'testall'
#
# Python test set, should exercise:
#      - all lexical and grammatical constructs
#      - all opcodes from "opcode.h"
#      - all operations on all object types
#      - all builtin functions
# Ideally also:
#      - all possible exception situations (Thank God we've got 'try')
#      - all boundary cases


TestFailed = 'testall -- test failed'          # Exception


#########################################################
# Part 1.  Test all lexical and grammatical constructs.
# This just tests whether the parser accepts them all.
#########################################################

print '1. Parser'

print '1.1 Tokens'

print '1.1.1 Backslashes'

# Backslash means line continuation:
x = 1 \
+ 1
if x <> 2: raise TestFailed, 'backslash for line continuation'

# Backslash does not means continuation in comments :\
x = 0
if x <> 0: raise TestFailed, 'backslash ending comment'

print '1.1.2 Number formats'

if 0xff <> 255: raise TestFailed, 'hex number'
if 0377 <> 255: raise TestFailed, 'octal number'
x = 3.14
x = 0.314
x = 3e14
x = 3E14
x = 3e-14

print '1.2 Grammar'

print 'single_input' # NEWLINE | simple_stmt | compound_stmt NEWLINE
# XXX can't test in a script -- this rule is only used when interactive

print 'file_input' # (NEWLINE | stmt)* ENDMARKER
# Being tested as this very moment this very module

print 'expr_input' # testlist NEWLINE
# XXX Hard to test -- used only in calls to input()

print 'eval_input' # testlist ENDMARKER
x = eval('1, 0 or 1')

print 'funcdef' # 'def' NAME parameters ':' suite
### parameters: '(' [fplist] ')'
### fplist: fpdef (',' fpdef)*
### fpdef: NAME | '(' fplist ')'
def f1(): pass
def f2(one_argument): pass
def f3(two, arguments): pass
def f4(two, (compound, (arguments))): pass

### stmt: simple_stmt | compound_stmt
### simple_stmt: expr_stmt | print_stmt  | pass_stmt | del_stmt | flow_stmt | import_stmt
# Tested below

print 'expr_stmt' # (exprlist '=')* exprlist NEWLINE
1
1, 2, 3
x = 1
x = 1, 2, 3
x = y = z = 1, 2, 3
x, y, z = 1, 2, 3
abc = a, b, c = x, y, z = xyz = 1, 2, (3, 4)
# NB these variables are deleted below

print 'print_stmt' # 'print' (test ',')* [test] NEWLINE
print 1, 2, 3
print 1, 2, 3,
print
print 0 or 1, 0 or 1,
print 0 or 1

print 'del_stmt' # 'del' exprlist NEWLINE
del abc
del x, y, (z, xyz)

print 'pass_stmt' # 'pass' NEWLINE
pass

print 'flow_stmt' # break_stmt | return_stmt | raise_stmt
# Tested below

print 'break_stmt' # 'break' NEWLINE
while 1: break

print 'return_stmt' # 'return' [testlist] NEWLINE
def g1(): return
def g2(): return 1
g1()
x = g2()

print 'raise_stmt' # 'raise' expr [',' expr] NEWLINE
try: raise RuntimeError, 'just testing'
except RuntimeError: pass
try: raise KeyboardInterrupt
except KeyboardInterrupt: pass

print 'import_stmt' # 'import' NAME (',' NAME)* NEWLINE | 'from' NAME 'import' ('*' | NAME (',' NAME)*) NEWLINE
[1]
import sys
[2]
import time, math
[3]
from time import sleep
[4]
from math import *
[5]
from sys import modules, path
[6]

### compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funcdef | classdef
# Tested below

print 'if_stmt' # 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
if 1: pass
if 1: pass
else: pass
if 0: pass
elif 0: pass
if 0: pass
elif 0: pass
elif 0: pass
elif 0: pass
else: pass

print 'while_stmt' # 'while' test ':' suite ['else' ':' suite]
while 0: pass
while 0: pass
else: pass

print 'for_stmt' # 'for' exprlist 'in' exprlist ':' suite ['else' ':' suite]
[1]
for i in 1, 2, 3: pass
[2]
for i, j, k in (): pass
else: pass
[3]

print 'try_stmt' # 'try' ':' suite (except_clause ':' suite)* ['finally' ':' suite]
### except_clause: 'except' [expr [',' expr]]
try: pass
try: 1/0
except RuntimeError: pass
try: 1/0
except EOFError: pass
except TypeError, msg: pass
except RuntimeError, msg: pass
except: pass
try: pass
finally: pass
try: 1/0
except: pass
finally: pass

print 'suite' # simple_stmt | NEWLINE INDENT NEWLINE* (stmt NEWLINE*)+ DEDENT
if 1: pass
if 1:
       pass
if 1:
       #
       #
       #
       pass
       pass
       #
       pass
       #

print 'test' # and_test ('or' and_test)*
### and_test: not_test ('and' not_test)*
### not_test: 'not' not_test | comparison
### comparison: expr (comp_op expr)*
### comp_op: '<'|'>'|'='|'>' '='|'<' '='|'<' '>'|'in'|'not' 'in'|'is'|'is' 'not'
if 1: pass
if 1 = 1: pass
if 1 < 1 > 1 = 1 >= 1 <= 1 <> 1 in 1 not in 1 is 1 is not 1: pass
if not 1 = 1 = 1: pass
if not 1 = 1 and 1 and 1: pass
if 1 and 1 or 1 and 1 and 1 or not 1 = 1 = 1 and 1: pass

print 'expr' # term (('+'|'-') term)*
x = 1
x = 1 + 1
x = 1 - 1 - 1
x = 1 - 1 + 1 - 1 + 1

print 'term' # factor (('*'|'/'|'%') factor)*
x = 1 * 1
x = 1 / 1
x = 1 % 1
x = 1 / 1 * 1 % 1

print 'factor' # ('+'|'-') factor | atom trailer*
### trailer: '(' [testlist] ')' | '[' subscript ']' | '.' NAME
### subscript: expr | [expr] ':' [expr]
x = +1
x = -1
x = 1
c = sys.path[0]
x = time.time()
x = sys.modules['time'].time()
a = '01234'
c = a[0]
c = a[0:5]
c = a[:5]
c = a[0:]
c = a[:]
c = a[-5:]
c = a[:-1]
c = a[-4:-3]

print 'atom' # '(' [testlist] ')' | '[' [testlist] ']' | '{' '}' | '`' testlist '`' | NAME | NUMBER | STRING
x = (1)
x = (1 or 2 or 3)
x = (1 or 2 or 3, 2, 3)
x = []
x = [1]
x = [1 or 2 or 3]
x = [1 or 2 or 3, 2, 3]
x = []
x = {}
x = `x`
x = x
x = 'x'
x = 123

### exprlist: expr (',' expr)* [',']
### testlist: test (',' test)* [',']
# These have been exercised enough above

print 'classdef' # 'class' NAME parameters ['=' baselist] ':' suite
### baselist: atom arguments (',' atom arguments)*
### arguments: '(' [testlist] ')'
class B(): pass
class C1() = B(): pass
class C2() = B(): pass
class D() = C1(), C2(), B(): pass
class C():
       def meth1(self): pass
       def meth2(self, arg): pass
       def meth3(self, (a1, a2)): pass


#########################################################
# Part 2.  Test all opcodes from "opcode.h"
#########################################################

print '2. Opcodes'
print 'XXX Not yet fully implemented'

print '2.1 try inside for loop'
n = 0
for i in range(10):
       n = n+i
       try: 1/0
       except NameError: pass
       except RuntimeError: pass
       except TypeError: pass
       finally: pass
       try: pass
       except: pass
       try: pass
       finally: pass
       n = n+i
if n <> 90:
       raise TestFailed, 'try inside for'


#########################################################
# Part 3.  Test all operations on all object types
#########################################################

print '3. Object types'
print 'XXX Not yet implemented'


#########################################################
# Part 4.  Test all built-in functions
#########################################################

print '4. Built-in functions'

print 'abs'
if abs(0) <> 0: raise TestFailed, 'abs(0)'
if abs(1234) <> 1234: raise TestFailed, 'abs(1234)'
if abs(-1234) <> 1234: raise TestFailed, 'abs(-1234)'
if abs(0.0) <> 0.0: raise TestFailed, 'abs(0.0)'
if abs(3.14) <> 3.14: raise TestFailed, 'abs(3.14)'
if abs(-3.14) <> 3.14: raise TestFailed, 'abs(-3.14)'

print 'dir'
if 'x' not in dir(): raise TestFailed, 'dir()'
if 'modules' not in dir(sys): raise TestFailed, 'dir(sys)'

print 'divmod'
if divmod(12, 7) <> (1, 5): raise TestFailed, 'divmod(12, 7)'
if divmod(-12, 7) <> (-2, 2): raise TestFailed, 'divmod(-12, 7)'
if divmod(12, -7) <> (-2, -2): raise TestFailed, 'divmod(12, -7)'
if divmod(-12, -7) <> (1, -5): raise TestFailed, 'divmod(-12, -7)'

print 'eval'
if eval('1+1') <> 2: raise TestFailed, 'eval(\'1+1\')'

print 'exec'
exec('z=1+1\n')
if z <> 2: raise TestFailed, 'exec(\'z=1+1\'\\n)'

print 'float'
if float(3.14) <> 3.14: raise TestFailed, 'float(3.14)'
if float(314) <> 314.0: raise TestFailed, 'float(314)'

print 'input'
# Can't test in a script

print 'int'
if int(100) <> 100: raise TestFailed, 'int(100)'
if int(3.14) <> 3: raise TestFailed, 'int(3.14)'

print 'len'
if len('123') <> 3: raise TestFailed, 'len(\'123\')'
if len(()) <> 0: raise TestFailed, 'len(())'
if len((1, 2, 3, 4)) <> 4: raise TestFailed, 'len((1, 2, 3, 4))'
if len([1, 2, 3, 4]) <> 4: raise TestFailed, 'len([1, 2, 3, 4])'
if len({}) <> 0: raise TestFailed, 'len({})'

print 'min'
if min('123123') <> '1': raise TestFailed, 'min(\'123123\')'
if min(1, 2, 3) <> 1: raise TestFailed, 'min(1, 2, 3)'
if min((1, 2, 3, 1, 2, 3)) <> 1: raise TestFailed, 'min((1, 2, 3, 1, 2, 3))'
if min([1, 2, 3, 1, 2, 3]) <> 1: raise TestFailed, 'min([1, 2, 3, 1, 2, 3])'

print 'max'
if max('123123') <> '3': raise TestFailed, 'max(\'123123\')'
if max(1, 2, 3) <> 3: raise TestFailed, 'max(1, 2, 3)'
if max((1, 2, 3, 1, 2, 3)) <> 3: raise TestFailed, 'max((1, 2, 3, 1, 2, 3))'
if max([1, 2, 3, 1, 2, 3]) <> 3: raise TestFailed, 'max([1, 2, 3, 1, 2, 3])'

print 'open'
print 'NB! This test creates a file named "@test" in the current directory.'
fp = open('@test', 'w')
fp.write('The quick brown fox jumps over the lazy dog')
fp.write('.\n')
fp.write('Dear John\n')
fp.write('XXX'*100)
fp.write('YYY'*100)
fp.close()
del fp
fp = open('@test', 'r')
if fp.readline() <> 'The quick brown fox jumps over the lazy dog.\n':
       raise TestFailed, 'readline()'
if fp.readline(4) <> 'Dear': raise TestFailed, 'readline(4) # short'
if fp.readline(100) <> ' John\n': raise TestFailed, 'readline(100)'
if fp.read(300) <> 'XXX'*100: raise TestFailed, 'read(300)'
if fp.read(1000) <> 'YYY'*100: raise TestFailed, 'read(1000) # truncate'
fp.close()
del fp

print 'range'
if range(3) <> [0, 1, 2]: raise TestFailed, 'range(3)'
if range(1, 5) <> [1, 2, 3, 4]: raise TestFailed, 'range(1, 5)'
if range(0) <> []: raise TestFailed, 'range(0)'
if range(-3) <> []: raise TestFailed, 'range(-3)'
if range(1, 10, 3) <> [1, 4, 7]: raise TestFailed, 'range(1, 10, 3)'
if range(5, -5, -3) <> [5, 2, -1, -4]: raise TestFailed, 'range(5, -5, -3)'

print 'raw_input'
savestdin = sys.stdin
try:
       sys.stdin = open('@test', 'r')
       if raw_input() <> 'The quick brown fox jumps over the lazy dog.':
               raise TestFailed, 'raw_input()'
       if raw_input('testing\n') <> 'Dear John':
               raise TestFailed, 'raw_input(\'testing\\n\')'
finally:
       sys.stdin = savestdin

print 'reload'
import string
reload(string)

print 'type'
if type('') <> type('123') or type('') = type(()):
       raise TestFailed, 'type()'


print 'Passed all tests.'

try:
       import mac
       unlink = mac.unlink
except NameError:
       try:
               import posix
               unlink = posix.unlink
       except NameError:
               pass

unlink('@test')
print 'Unlinked @test'
