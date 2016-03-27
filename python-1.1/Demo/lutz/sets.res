ld.so: warning: /usr/lib/libc.so.1.6 has older revision than expected 8
a b c d e f g
a b c d e f g
1 0

table =>
   tuple => [age]=0 [name]='x' [stats]=[1, 2, 3]

table =>
   tuple => [age]=0 [name]='x' [stats]=[1, 2, 3]
   tuple => [age]='y' [name]=1 [stats]=[4, 5, 6]
   tuple => [age]='z' [name]=2 [stats]=[7, 8]

table =>
   tuple => {'name': 'mark', 'job': 'engineer'}
   tuple => {'name': 'amrit', 'job': 'engineer'}
   tuple => {'name': 'sunil', 'job': 'manager'}
   tuple => {'name': 'marc', 'job': 'prez'}
   tuple => {'name': 'martin', 'job': 'architect'}
   tuple => {'name': 'jeff', 'job': 'engineer'}
   tuple => {'name': 'eve', 'job': 'administrator'}

table =>
   tuple => {'name': 'mark', 'job': 'engineer'}
   tuple => {'name': 'amrit', 'job': 'engineer'}
   tuple => {'name': 'jeff', 'job': 'engineer'}

table =>
   tuple => {'pay': (25000, 60000), 'name': 'mark', 'job': 'engineer'}
   tuple => {'pay': (25000, 60000), 'name': 'amrit', 'job': 'engineer'}
   tuple => {'pay': (50000, 'XXX'), 'name': 'sunil', 'job': 'manager'}
   tuple => {'pay': 'see figure 1', 'name': 'marc', 'job': 'prez'}
   tuple => {'pay': None, 'name': 'martin', 'job': 'architect'}
   tuple => {'pay': (25000, 60000), 'name': 'jeff', 'job': 'engineer'}

table =>
   tuple => [name]='mark' [pay]=(25000, 60000) [job]='engineer'
   tuple => [name]='amrit' [pay]=(25000, 60000) [job]='engineer'
   tuple => [name]='sunil' [pay]=(50000, 'XXX') [job]='manager'
   tuple => [name]='marc' [pay]='see figure 1' [job]='prez'
   tuple => [name]='martin' [pay]=None [job]='architect'
   tuple => [name]='jeff' [pay]=(25000, 60000) [job]='engineer'

table =>
   tuple => {'job': 'engineer'}
   tuple => {'job': 'manager'}
   tuple => {'job': 'prez'}
   tuple => {'job': 'architect'}
   tuple => {'job': 'administrator'}

table =>
   tuple => {'name': 'mark'}
   tuple => {'name': 'amrit'}
   tuple => {'name': 'jeff'}

table =>
   tuple => [job]='manager' [name]='sunil'
   tuple => [job]='prez' [name]='marc'

table =>
   tuple => [job]='manager' [name]='sunil'
   tuple => [job]='manager' [name]='steve'

table =>
   tuple => [name]='mark' [job]='engineer'
   tuple => [name]='marc' [job]='prez'
   tuple => [name]='martin' [job]='architect'

table =>
   tuple => [name]='sunil' [job]='manager'
   tuple => [name]='marc' [job]='prez'

table =>
   tuple => [name]='sunil' [job]='manager'
   tuple => [name]='marc' [job]='prez'
   tuple => [name]='eve' [job]='administrator'

{'job': 'administrator'}

table =>
   tuple => {'name': 'mark', 'pay': (25000, 60000)}
   tuple => {'name': 'amrit', 'pay': (25000, 60000)}
   tuple => {'name': 'sunil', 'pay': (50000, 'XXX')}
   tuple => {'name': 'marc', 'pay': 'see figure 1'}
   tuple => {'name': 'martin', 'pay': None}
   tuple => {'name': 'jeff', 'pay': (25000, 60000)}

table =>
   tuple => {'name': 'sunil', 'pay': (50000, 'XXX')}

table =>
   tuple => [pay]=(25000, 60000) [job_1]='engineer' [job]='engineer' [name]='mark'
   tuple => [pay]=(25000, 60000) [job_1]='engineer' [job]='engineer' [name]='amrit'
   tuple => [pay]=(25000, 60000) [job_1]='manager' [job]='engineer' [name]='sunil'
   tuple => [pay]=(25000, 60000) [job_1]='engineer' [job]='engineer' [name]='john'
   tuple => [pay]=(25000, 60000) [job_1]='manager' [job]='engineer' [name]='steve'
   tuple => [pay]=(50000, 'XXX') [job_1]='engineer' [job]='manager' [name]='mark'
   tuple => [pay]=(50000, 'XXX') [job_1]='engineer' [job]='manager' [name]='amrit'
   tuple => [pay]=(50000, 'XXX') [job_1]='manager' [job]='manager' [name]='sunil'
   tuple => [pay]=(50000, 'XXX') [job_1]='engineer' [job]='manager' [name]='john'
   tuple => [pay]=(50000, 'XXX') [job_1]='manager' [job]='manager' [name]='steve'
   tuple => [pay]=None [job_1]='engineer' [job]='architect' [name]='mark'
   tuple => [pay]=None [job_1]='engineer' [job]='architect' [name]='amrit'
   tuple => [pay]=None [job_1]='manager' [job]='architect' [name]='sunil'
   tuple => [pay]=None [job_1]='engineer' [job]='architect' [name]='john'
   tuple => [pay]=None [job_1]='manager' [job]='architect' [name]='steve'
   tuple => [pay]='see figure 1' [job_1]='engineer' [job]='prez' [name]='mark'
   tuple => [pay]='see figure 1' [job_1]='engineer' [job]='prez' [name]='amrit'
   tuple => [pay]='see figure 1' [job_1]='manager' [job]='prez' [name]='sunil'
   tuple => [pay]='see figure 1' [job_1]='engineer' [job]='prez' [name]='john'
   tuple => [pay]='see figure 1' [job_1]='manager' [job]='prez' [name]='steve'

table =>
   tuple => [name_1]='mark' [name]='mark' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='amrit' [name]='mark' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='sunil' [name]='mark' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='john' [name]='mark' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='steve' [name]='mark' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='mark' [name]='amrit' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='amrit' [name]='amrit' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='sunil' [name]='amrit' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='john' [name]='amrit' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='steve' [name]='amrit' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='mark' [name]='sunil' [job_1]='engineer' [job]='manager'
   tuple => [name_1]='amrit' [name]='sunil' [job_1]='engineer' [job]='manager'
   tuple => [name_1]='sunil' [name]='sunil' [job_1]='manager' [job]='manager'
   tuple => [name_1]='john' [name]='sunil' [job_1]='engineer' [job]='manager'
   tuple => [name_1]='steve' [name]='sunil' [job_1]='manager' [job]='manager'
   tuple => [name_1]='mark' [name]='marc' [job_1]='engineer' [job]='prez'
   tuple => [name_1]='amrit' [name]='marc' [job_1]='engineer' [job]='prez'
   tuple => [name_1]='sunil' [name]='marc' [job_1]='manager' [job]='prez'
   tuple => [name_1]='john' [name]='marc' [job_1]='engineer' [job]='prez'
   tuple => [name_1]='steve' [name]='marc' [job_1]='manager' [job]='prez'
   tuple => [name_1]='mark' [name]='martin' [job_1]='engineer' [job]='architect'
   tuple => [name_1]='amrit' [name]='martin' [job_1]='engineer' [job]='architect'
   tuple => [name_1]='sunil' [name]='martin' [job_1]='manager' [job]='architect'
   tuple => [name_1]='john' [name]='martin' [job_1]='engineer' [job]='architect'
   tuple => [name_1]='steve' [name]='martin' [job_1]='manager' [job]='architect'
   tuple => [name_1]='mark' [name]='jeff' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='amrit' [name]='jeff' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='sunil' [name]='jeff' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='john' [name]='jeff' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='steve' [name]='jeff' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='mark' [name]='eve' [job_1]='engineer' [job]='administrator'
   tuple => [name_1]='amrit' [name]='eve' [job_1]='engineer' [job]='administrator'
   tuple => [name_1]='sunil' [name]='eve' [job_1]='manager' [job]='administrator'
   tuple => [name_1]='john' [name]='eve' [job_1]='engineer' [job]='administrator'
   tuple => [name_1]='steve' [name]='eve' [job_1]='manager' [job]='administrator'

table =>
   tuple => [name_1]='mark' [name]='mark' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='amrit' [name]='mark' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='sunil' [name]='mark' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='john' [name]='mark' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='steve' [name]='mark' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='mark' [name]='amrit' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='amrit' [name]='amrit' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='sunil' [name]='amrit' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='john' [name]='amrit' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='steve' [name]='amrit' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='mark' [name]='sunil' [job_1]='engineer' [job]='manager'
   tuple => [name_1]='amrit' [name]='sunil' [job_1]='engineer' [job]='manager'
   tuple => [name_1]='sunil' [name]='sunil' [job_1]='manager' [job]='manager'
   tuple => [name_1]='john' [name]='sunil' [job_1]='engineer' [job]='manager'
   tuple => [name_1]='steve' [name]='sunil' [job_1]='manager' [job]='manager'
   tuple => [name_1]='mark' [name]='marc' [job_1]='engineer' [job]='prez'
   tuple => [name_1]='amrit' [name]='marc' [job_1]='engineer' [job]='prez'
   tuple => [name_1]='sunil' [name]='marc' [job_1]='manager' [job]='prez'
   tuple => [name_1]='john' [name]='marc' [job_1]='engineer' [job]='prez'
   tuple => [name_1]='steve' [name]='marc' [job_1]='manager' [job]='prez'
   tuple => [name_1]='mark' [name]='martin' [job_1]='engineer' [job]='architect'
   tuple => [name_1]='amrit' [name]='martin' [job_1]='engineer' [job]='architect'
   tuple => [name_1]='sunil' [name]='martin' [job_1]='manager' [job]='architect'
   tuple => [name_1]='john' [name]='martin' [job_1]='engineer' [job]='architect'
   tuple => [name_1]='steve' [name]='martin' [job_1]='manager' [job]='architect'
   tuple => [name_1]='mark' [name]='jeff' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='amrit' [name]='jeff' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='sunil' [name]='jeff' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='john' [name]='jeff' [job_1]='engineer' [job]='engineer'
   tuple => [name_1]='steve' [name]='jeff' [job_1]='manager' [job]='engineer'
   tuple => [name_1]='mark' [name]='eve' [job_1]='engineer' [job]='administrator'
   tuple => [name_1]='amrit' [name]='eve' [job_1]='engineer' [job]='administrator'
   tuple => [name_1]='sunil' [name]='eve' [job_1]='manager' [job]='administrator'
   tuple => [name_1]='john' [name]='eve' [job_1]='engineer' [job]='administrator'
   tuple => [name_1]='steve' [name]='eve' [job_1]='manager' [job]='administrator'

table =>
   tuple => [name]='mark'
   tuple => [name]='amrit'
   tuple => [name]='sunil'
   tuple => [name]='marc'
   tuple => [name]='martin'
   tuple => [name]='jeff'
   tuple => [name]='eve'

table =>
   tuple => [name_1]='mark' [name]='mark'
   tuple => [name_1]='amrit' [name]='mark'
   tuple => [name_1]='sunil' [name]='mark'
   tuple => [name_1]='john' [name]='mark'
   tuple => [name_1]='steve' [name]='mark'
   tuple => [name_1]='mark' [name]='amrit'
   tuple => [name_1]='amrit' [name]='amrit'
   tuple => [name_1]='sunil' [name]='amrit'
   tuple => [name_1]='john' [name]='amrit'
   tuple => [name_1]='steve' [name]='amrit'
   tuple => [name_1]='mark' [name]='sunil'
   tuple => [name_1]='amrit' [name]='sunil'
   tuple => [name_1]='sunil' [name]='sunil'
   tuple => [name_1]='john' [name]='sunil'
   tuple => [name_1]='steve' [name]='sunil'
   tuple => [name_1]='mark' [name]='marc'
   tuple => [name_1]='amrit' [name]='marc'
   tuple => [name_1]='sunil' [name]='marc'
   tuple => [name_1]='john' [name]='marc'
   tuple => [name_1]='steve' [name]='marc'
   tuple => [name_1]='mark' [name]='martin'
   tuple => [name_1]='amrit' [name]='martin'
   tuple => [name_1]='sunil' [name]='martin'
   tuple => [name_1]='john' [name]='martin'
   tuple => [name_1]='steve' [name]='martin'
   tuple => [name_1]='mark' [name]='jeff'
   tuple => [name_1]='amrit' [name]='jeff'
   tuple => [name_1]='sunil' [name]='jeff'
   tuple => [name_1]='john' [name]='jeff'
   tuple => [name_1]='steve' [name]='jeff'
   tuple => [name_1]='mark' [name]='eve'
   tuple => [name_1]='amrit' [name]='eve'
   tuple => [name_1]='sunil' [name]='eve'
   tuple => [name_1]='john' [name]='eve'
   tuple => [name_1]='steve' [name]='eve'

table =>
   tuple => [name]='amrit' [job]='engineer'
   tuple => [name]='eve' [job]='administrator'
   tuple => [name]='jeff' [job]='engineer'
   tuple => [name]='marc' [job]='prez'
   tuple => [name]='mark' [job]='engineer'
   tuple => [name]='martin' [job]='architect'
   tuple => [name]='sunil' [job]='manager'

table =>
   tuple => [name]='amrit' [job]='engineer'
   tuple => [name]='eve' [job]='administrator'
   tuple => [name]='jeff' [job]='engineer'
   tuple => [name]='marc' [job]='prez'
   tuple => [name]='mark' [job]='engineer'
   tuple => [name]='martin' [job]='architect'
   tuple => [name]='sunil' [job]='manager'

table =>
   tuple => [name]='amrit' [job]='engineer'
   tuple => [name]='john' [job]='engineer'
   tuple => [name]='mark' [job]='engineer'
   tuple => [name]='steve' [job]='manager'
   tuple => [name]='sunil' [job]='manager'

{'name': 'marc', 'job': 'prez'}
{'name': 'martin', 'job': 'architect'}
{'name': 'jeff', 'job': 'engineer'}
{'name': 'eve', 'job': 'administrator'}

{'name': 'mark', 'job': 'engineer'}
{'name': 'amrit', 'job': 'engineer'}
{'name': 'sunil', 'job': 'manager'}

{'name': 'mark', 'job': 'engineer'}
{'name': 'amrit', 'job': 'engineer'}
{'name': 'sunil', 'job': 'manager'}
{'name': 'marc', 'job': 'prez'}
{'name': 'martin', 'job': 'architect'}
{'name': 'jeff', 'job': 'engineer'}
{'name': 'eve', 'job': 'administrator'}
{'name': 'john', 'job': 'engineer'}
{'name': 'steve', 'job': 'manager'}
1
1
0
1
0
1

table =>
   tuple => [name]='alpha' [use]='glue' [type]='proced' [rank]=3
   tuple => [name]='python' [use]='rad' [type]='proced' [rank]=1
   tuple => [name]='icon' [use]='rad' [type]='proced' [rank]=1
   tuple => [name]='smalltalk' [use]='oop' [type]='object' [rank]=4
   tuple => [name]='dylan' [use]='glue' [type]='object' [rank]=7
   tuple => [name]='self' [use]='oop' [type]='object' [rank]=7
   tuple => [name]='d' [use]='glue' [type]='unknown' [rank]=7

table =>
   tuple => [name]='prolog' [class]='ai'
   tuple => [name]='prolog' [class]='compilers'
   tuple => [name]='alpha' [class]='compilers'
   tuple => [name]='python' [class]='compilers'
   tuple => [name]='icon' [class]='compilers'
   tuple => [name]='scheme' [class]='ai'
   tuple => [name]='smalltalk' [class]='simulation'
   tuple => [name]='dylan' [class]='simulation'
   tuple => [name]='self' [class]='simulation'
   tuple => [name]='rexx' [class]='compilers'
   tuple => [name]='tcl' [class]='compilers'
   tuple => [name]='lisp' [class]='ai'
   tuple => [name]='perl' [class]='compilers'

table =>
   tuple => {'name': 'prolog', 'prof': 'travis'}
   tuple => {'name': 'prolog', 'prof': 'horwitz'}
   tuple => {'name': 'alpha', 'prof': 'horwitz'}
   tuple => {'name': 'python', 'prof': 'horwitz'}
   tuple => {'name': 'icon', 'prof': 'horwitz'}
   tuple => {'name': 'scheme', 'prof': 'travis'}
   tuple => {'name': 'rexx', 'prof': 'horwitz'}
   tuple => {'name': 'tcl', 'prof': 'horwitz'}
   tuple => {'name': 'lisp', 'prof': 'travis'}
   tuple => {'name': 'perl', 'prof': 'horwitz'}

table =>
   tuple => {'class': 'ai'}
   tuple => {'class': 'compilers'}

table =>
   tuple => [name]='icon' [rank]=1
   tuple => [name]='python' [rank]=1
   tuple => [name]='scheme' [rank]=2

table =>
   tuple => [name]='lisp' [rank]=3
   tuple => [name]='alpha' [rank]=3

table =>
   tuple => [name]='smalltalk' [rank]=4
   tuple => [name]='prolog' [rank]=5
   tuple => [name]='tcl' [rank]=6
   tuple => [name]='perl' [rank]=7
   tuple => [name]='d' [rank]=7
   tuple => [name]='rexx' [rank]=7
   tuple => [name]='self' [rank]=7
   tuple => [name]='dylan' [rank]=7

table =>
   tuple => [name]='prolog' [rank]=5 [use]='aliens' [type]='logic'
   tuple => [name]='tcl' [rank]=6 [use]='shell' [type]='proced'
   tuple => [name]='perl' [rank]=7 [use]='shell' [type]='proced'
   tuple => [name]='d' [rank]=7 [use]='glue' [type]='unknown'
   tuple => [name]='rexx' [rank]=7 [use]='shell' [type]='proced'
   tuple => [name]='self' [rank]=7 [use]='oop' [type]='object'
   tuple => [name]='dylan' [rank]=7 [use]='glue' [type]='object'

table =>

table =>
   tuple => [use]='rad' [type]='proced' [name]='python' [rank]=1
   tuple => [use]='rad' [type]='proced' [name]='icon' [rank]=1

table =>
   tuple => [use]='aliens' [type]='logic' [name]='prolog' [rank]=5
   tuple => [use]='glue' [type]='proced' [name]='alpha' [rank]=3
   tuple => [use]='rad' [type]='proced' [name]='python' [rank]=1
   tuple => [use]='rad' [type]='proced' [name]='icon' [rank]=1
   tuple => [use]='aliens' [type]='funct' [name]='scheme' [rank]=2
   tuple => [use]='oop' [type]='object' [name]='smalltalk' [rank]=4
   tuple => [use]='shell' [type]='proced' [name]='tcl' [rank]=6
   tuple => [use]='aliens' [type]='funct' [name]='lisp' [rank]=3
   tuple => [use]='shell' [type]='proced' [name]='perl' [rank]=7

table =>
   tuple => [use]='rad' [type]='proced' [name]='python' [rank]=1
   tuple => [use]='rad' [type]='proced' [name]='icon' [rank]=1
   tuple => [use]='oop' [type]='object' [name]='smalltalk' [rank]=4
   tuple => [use]='glue' [type]='object' [name]='dylan' [rank]=7
   tuple => [use]='oop' [type]='object' [name]='self' [rank]=7

table =>
   tuple => [name]='python'
   tuple => [name]='icon'

['a', 'c', 'e', 'g']
['a', 'c', 'e', 'g']
1 1 0
1 0

['h', 'e', 'l', 'p']
['h', 'e', 'p', 'l']
['h', 'l', 'e', 'p']
['h', 'l', 'p', 'e']
['h', 'p', 'e', 'l']
['h', 'p', 'l', 'e']
['e', 'h', 'l', 'p']
['e', 'h', 'p', 'l']
['e', 'l', 'h', 'p']
['e', 'l', 'p', 'h']
['e', 'p', 'h', 'l']
['e', 'p', 'l', 'h']
['l', 'h', 'e', 'p']
['l', 'h', 'p', 'e']
['l', 'e', 'h', 'p']
['l', 'e', 'p', 'h']
['l', 'p', 'h', 'e']
['l', 'p', 'e', 'h']
['p', 'h', 'e', 'l']
['p', 'h', 'l', 'e']
['p', 'e', 'h', 'l']
['p', 'e', 'l', 'h']
['p', 'l', 'h', 'e']
['p', 'l', 'e', 'h']

< [] >

< ['h'] ['e'] ['l'] ['p'] >

< ['h', 'e'] ['h', 'l'] ['h', 'p'] ['e', 'l'] ['e', 'p'] ['l', 'p'] >

< ['h', 'e', 'l'] ['h', 'e', 'p'] ['h', 'l', 'p'] ['e', 'l', 'p'] >

< ['h', 'e', 'l', 'p'] >

< >

< [] >

< ['h'] ['e'] ['l'] ['p'] >

< ['h', 'e'] ['h', 'l'] ['h', 'p'] ['e', 'h'] ['e', 'l'] ['e', 'p'] ['l', 'h'] ['l', 'e'] ['l', 'p'] ['p', 'h'] ['p', 'e'] ['p', 'l'] >

< ['h', 'e', 'l'] ['h', 'e', 'p'] ['h', 'l', 'e'] ['h', 'l', 'p'] ['h', 'p', 'e'] ['h', 'p', 'l'] ['e', 'h', 'l'] ['e', 'h', 'p'] ['e', 'l', 'h'] ['e', 'l', 'p'] ['e', 'p', 'h'] ['e', 'p', 'l'] ['l', 'h', 'e'] ['l', 'h', 'p'] ['l', 'e', 'h'] ['l', 'e', 'p'] ['l', 'p', 'h'] ['l', 'p', 'e'] ['p', 'h', 'e'] ['p', 'h', 'l'] ['p', 'e', 'h'] ['p', 'e', 'l'] ['p', 'l', 'h'] ['p', 'l', 'e'] >

< ['h', 'e', 'l', 'p'] ['h', 'e', 'p', 'l'] ['h', 'l', 'e', 'p'] ['h', 'l', 'p', 'e'] ['h', 'p', 'e', 'l'] ['h', 'p', 'l', 'e'] ['e', 'h', 'l', 'p'] ['e', 'h', 'p', 'l'] ['e', 'l', 'h', 'p'] ['e', 'l', 'p', 'h'] ['e', 'p', 'h', 'l'] ['e', 'p', 'l', 'h'] ['l', 'h', 'e', 'p'] ['l', 'h', 'p', 'e'] ['l', 'e', 'h', 'p'] ['l', 'e', 'p', 'h'] ['l', 'p', 'h', 'e'] ['l', 'p', 'e', 'h'] ['p', 'h', 'e', 'l'] ['p', 'h', 'l', 'e'] ['p', 'e', 'h', 'l'] ['p', 'e', 'l', 'h'] ['p', 'l', 'h', 'e'] ['p', 'l', 'e', 'h'] >

< >

< [1, 2, 3] [1, 3, 2] [2, 1, 3] [2, 3, 1] [3, 1, 2] [3, 2, 1] >
[['a', 'l', 'p'], ['a', 'p', 'l'], ['l', 'a', 'p'], ['l', 'p', 'a'], ['p', 'a', 'l'], ['p', 'l', 'a']]

< a l p p o >

< o p p l a >

< a l o p p >
['a', 'l', 'p', 'p', 'o']
alppo

[2, 4, 6]
[2, 4, 6]
[2, 4, 6]
[2, 4, 6]
[2, 4, 6]
[2, 4, 6]
[2, 4, 6]

4 ['a', 'b', 'c', 'd', 'e', 'f', 'g'] ['a', 'c'] ['a', 'b', 'c', 'd', 'a', 'b', 'c', 'd', 'a', 'b', 'c', 'd']
a ['a', 'b']
['z', 'c', 'd']
0 1
0 1
['a', 'b', 'c', 'd', 'e', 'x', 'y']
['a', 'c', 'e']
['b', 'c']
['e', 'd', 'c', 'b', 'a', 'a', 'x', 'e', 'd', 'y']
['a', 'e']
['a', 'b', 'c', 'd', 'e', 'z', 'x', 'y']
['b']
['a', 'b', 'c', 'd', 'e', 'a', 'z', 'c', 'e', 'a', 'x', 'e', 'd', 'y']
['b']

< a b c d e z >
None
