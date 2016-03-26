# Python to C -- from the parser output


import parser
import token
import symbol
import sys
import getopt


def main():
    opts, args = getopt.getopt(sys.argv[1:], '')
    if args:
	filename = args[0]
    else:
	filename = 'testf.py'
    root = parser.parsefile(filename)
    g = Generator(root)
    g.go()


class Formatter:

    def __init__(self):
	self.file = sys.stdout
	self.atbol = 0
	self.level = 0

    def indent(self):
	self.level = self.level + 1

    def dedent(self):
	self.level = self.level - 1

    def puts(self, fmt, *args):
	self.vputs(fmt, args)

    def vputs(self, fmt, args):
	if self.atbol: self.file.write('    ' * self.level)
	self.file.write(fmt % args)
	self.atbol = (fmt[-1:] == '\n')


class Generator(Formatter):

    def __init__(self, root):
	Formatter.__init__(self)
	self.stdc = 0
	self.root = root

    def go(self):
	self.dispatch(self.root)

    def llputs(self, fmt, *args):
	Formatter.vputs(self, fmt, args)

    def vputs(self, fmt, args):
	# Like Formatter.vputs but recognizes %n to dispatch a node
	# and handles { } \b \t \n differently
	iarg = 0
	i = 0
	n = len(fmt)
	start = 0
	while i < n:
	    c = fmt[i]
	    if c not in '%{}\n\b\t':
		i = i+1
		continue
	    if start < i:
		self.llputs(fmt[start:i])
		start = i
	    if c != '%':
		if c in '\b}': self.dedent()
		if c not in '\b\t': self.llputs(c)
		if c in '{\t': self.indent()
		start = i = i+1
		continue
	    i = i+1
	    while i < n and fmt[i] in '+-*#.0123456789 ':
		i = i+1
	    if i >= n:
		break
	    c = fmt[i]
	    i = i+1
	    if c == '%':
		self.llputs('%%')
	    elif c == 'n':
		self.dispatch(args[iarg])
		iarg = iarg + 1
	    else:
		self.llputs(fmt[start:i], args[iarg])
		iarg = iarg + 1
	    start = i
	if start < n:
	    self.llputs(fmt[start:n])

    def dispatch(self, node):
	sym = node[0]
	if sym < token.N_TOKENS:
	    name = token.tok_name[sym]
	else:
	    name = symbol.sym_name[sym]
	if hasattr(self, name):
	    apply(getattr(self, name), node[1:])
	else:
	    self.puts('/* %s unknown */\n', name)

    def nop(self, *children):
	pass

    NEWLINE = nop
    INDENT = nop
    DEDENT = nop
    ENDMARKER = nop
    pass_stmt = nop

    def passthru(self, *children):
	for child in children:
	    self.dispatch(child)

    file_input = passthru
    stmt = passthru
    compound_stmt = passthru
    suite = passthru
    simple_stmt = passthru
    small_stmt = passthru
    flow_stmt = passthru

    def funcdef(self, *children):
	(namesymbol, namestring) = children[1]
	parms = children[2]
	body = children[4]
	parmchildren = parms[1:]
	if len(parmchildren) == 3:
	    self.scan_arguments(parmchildren[1])
	else:
	    self.args = []		# list of (name, type) pairs
	self.puts('\nint %s(', namestring)
	if self.stdc:
	    sep = ''
	    for argname, argtype in self.args:
		self.puts('%s%s %s', sep, argtype, argname)
		sep = ', '
	    self.puts(')\n')
	else:
	    sep = ''
	    for argname, argtype in self.args:
		self.puts('%s%s', sep, argname)
		sep = ', '
	    self.puts(')\n\t')
	    for argname, argtype in self.args:
		self.puts('%s %s;\n', argtype, argname)
	    self.puts('\b')
	self.puts('{\n')
	self.vars = []
	self.find_variables(body)
	for varname, vartype in self.vars:
	    self.puts('%s %s;\n', vartype, varname)
	self.puts('%n}\n', body)

    def scan_arguments(self, node):
	self.args = []
	children = node[1:]
	for child in children:
	    if child[0] == symbol.fpdef:
		subchildren = child[1:]
		if len(subchildren) != 1:
		    self.puts('/* nested parameters not supported */')
		else:
		    subchild = subchildren[0]
		    namestring = subchild[1]
		    self.args.append((namestring, 'int'))

    def find_variables(self, node):
	sym = node[0]
	if sym < token.N_TOKENS:
	    return
	children = node[1:]
	if sym == symbol.expr_stmt:
	    for i in range(0, len(children)-2, 2):
		self.add_variables(children[i], 'int')
	elif sym == symbol.for_stmt:
	    self.add_variables(children[1], 'int')
	    for child in children[5:]:
		self.find_variables(child)
	elif sym == symbol.funcdef:
	    pass
	elif sym == symbol.classdef:
	    pass
	else:
	    for child in children:
		self.find_variables(child)

    def add_variables(self, node, vartype):
	node = self.strip_trivial(node)
	if node[0] == token.NAME:
	    entry = (node[1], vartype)
	    if entry not in self.vars and entry not in self.args:
		self.vars.append(entry)

    def print_stmt(self, *children):
	args = []
	format = ''
	i = 1
	while i < len(children):
	    s = self.test_string_literal(children[i])
	    if s is not None:
		s = eval(s)		# Not quite, but close enough for now
		format = format + s + ' '
	    else:
		args.append(children[i])
		format = format + '%d '
	    i = i+2
	if children[-1][0] != token.COMMA:
	    if format[-1:] == ' ': format = format[:-1]
	    format = format + '\\n'
	self.puts('printf("%s"', format)
	for arg in args:
	    self.puts(', %n', arg)
	self.puts(');\n')

    def strip_trivial(self, node):
	while 1:
	    sym = node[0]
	    children = node[1:]
	    if sym == symbol.atom and children[0][0] == token.LPAR and \
		  len(children) == 3:
		node = children[1]
	    elif sym > token.N_TOKENS and len(children) == 1:
		node = children[0]
	    else:
		break
	return node

    def test_string_literal(self, node):
	node = self.strip_trivial(node)
	if node[0] == token.STRING:
	    return node[1]
	else:
	    return None

    def operator_list(self, children):
	for child in children:
	    if child[0] < token.N_TOKENS:
		self.puts(' %s ', child[1])
	    else:
		self.dispatch(child)

    def va_operator_list(self, *children):
	self.operator_list(children)

    def separated_list(self, children, sep):
	for i in range(0, len(children), 2):
	    if i > 0: self.puts(sep)
	    self.dispatch(children[i])

    def return_stmt(self, *children):
	if len(children) == 1:
	    self.puts('return;\n')
	else:
	    self.puts('return %n;\n', children[1])

    def break_stmt(self, *children):
	self.puts('break;\n')

    def continue_stmt(self, *children):
	self.puts('continue;\n')

    def expr_stmt(self, *children):
	self.separated_list(children, ' = ')
	self.puts(';\n')

    def if_stmt(self, *children):
	i = 0
	while i+3 < len(children):
	    test = children[i+1]
	    suite = children[i+3]
	    if i > 0: self.puts('else ')
	    self.puts('if (%n) {\n%n}\n', test, suite)
	    i = i+4
	if i+2 < len(children):
	    suite = children[i+2]
	    self.puts('else {\n%n}\n', suite)

    def while_stmt(self, *children):
	test = children[1]
	suite = children[3]
	if len(children) > 6:		# while...else form
	    elsuite = children[6]
	    self.puts(
		  'while (1) {\nif (%n) {\n%n}\nelse {\n%nbreak;\n}\n}\n',
		  test, suite, elsuite)
	else:
	    self.puts('while (%n) {\n%n}\n', test, suite)

    def for_stmt(self, *children):
	variable = children[1]
	sequence = children[3]
	suite = children[5]
	if len(children) > 8:		# for...else form
	    elsuite = children[8]
	else:
	    elsuite = None
	control = self.test_range(sequence)
	if not control:
	    self.puts('/* too complicated for loop */\n')
	elif not elsuite:
	    start, stop, step = control
	    if not step:
		self.puts('for (%n = %n; %n < %n; %n++) ',
		      variable, start, variable, stop, variable)
	    else:
		self.puts('for (%n = %n; %n * (%n) < (%n) * (%n); %n += %n) ',
		      variable, start,
		      variable, step, stop, step,
		      variable, step)
	    self.puts('{\n%n}\n', suite)
	else:
	    start, stop, step = control
	    self.puts('%n = %n;\nwhile (1) {\n', variable, start)
	    if not step:
		self.puts('if (%n < %n) ', variable, stop)
	    else:
		self.puts('if (%n * (%n) < (%n) * (%n)) ',
		      variable, step, stop, step)
	    self.puts('{\n%n', suite)
	    if not step:
		self.puts('%n++;\n', variable)
	    else:
		self.puts('%n = %n + %n\n', variable, variable, step)
	    self.puts('}\nelse {\n%nbreak;\n}\n}\n', elsuite)

    def test_range(self, node):
	node = self.strip_trivial(node)
	if node[0] == symbol.factor:
	    children = node[1:]
	    if len(children) == 2 and children[0][0] == symbol.atom and \
		  children[1][0] == symbol.trailer:
		atom, trailer = children
		atom = self.strip_trivial(atom)
		if atom[0] == token.NAME and atom[1] == 'range':
		    children = trailer[1:]
		    if children[0][0] == token.LPAR and len(children) == 3:
			testlist = children[1]
			sym = testlist[0]
			children = testlist[1:]
			n = (len(testlist)+1) / 2
			if 1 <= n <= 3:
			    start = (token.NUMBER, '0')
			    step = None	# Special case
			    if n == 1:
				stop = children[0]
			    elif n == 2:
				start = children[0]
				stop = children[2]
			    elif n == 3:
				start = children[0]
				stop = children[2]
				step = children[4]
			    return start, stop, step
	return None

    def testlist(self, *children):
	self.separated_list(children, ', ')

    def test(self, *children):
	self.separated_list(children, ' || ')

    def and_test(self, *children):
	self.separated_list(children, ' && ')

    def not_test(self, *children):
	if len(children) == 2:
	    self.puts('!(%n)', children[1])
	else:
	    self.dispatch(children[0])

    def comparison(self, *children):
	if len(children) > 3:
	    self.puts('/* non-trivial comparison */')
	else:
	    self.operator_list(children)

    def comp_op(self, *children):
	child = children[0]
	if len(children) > 1 or child[0] == token.NAME:
	    self.puts(' /* unhandled comparison */ ')
	else:
	    s = child[1]
	    if s == '<>': s = '!='
	    self.puts(' %s ', s)

    exprlist = testlist
    expr = va_operator_list
    xor_expr = va_operator_list
    and_expr = va_operator_list
    shift_expr = va_operator_list
    arith_expr = va_operator_list
    factor = va_operator_list
    term = va_operator_list

    def atom(self, *children):
	child = children[0]
	childsymbol = child[0]
	if childsymbol in (token.NAME, token.NUMBER, token.STRING):
	    self.dispatch(child)
	elif childsymbol == token.LPAR and len(children) == 3:
	    self.puts('(%n)', children[1])
	else:
	    self.puts('/* unhandled atom */')

    def trailer(self, *children):
	child = children[0]
	csym = child[0]
	if csym == token.LPAR:
	    if len(children) == 3:
		self.puts('(%n)', children[1])
	    else:
		self.puts('()')
	elif csym == token.LSQB:
	    if len(children) == 3:
		self.puts('[%n]', children[1])
	    else:
		self.puts('[]')
	elif csym == token.DOT:
	    self.puts('.%n', children[1])
	else:
	    self.puts('/* XXX unexpected trailer */')

    def subscript(self, *children):
	if len(children) == 1:
	    self.dispatch(children[0])
	else:
	    self.puts('/* slice not supported */')

    def STRING(self, child):
	self.puts('%s', child)

    def NUMBER(self, child):
	self.puts('%s', child)

    def NAME(self, child):
	self.puts('%s', child)

main()
