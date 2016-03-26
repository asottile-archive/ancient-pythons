import os
import string
import sys
sys.path.append(os.path.join(os.getcwd(), 'bgen'))

def main():
	what = raw_input("scan[1] or support[2]? (default 1) ")
	what = string.strip(what)
	if what:
		n = string.atoi(what)
	else:
		n = 1
	if n == 1:
		runall("scan", 1)
	elif n == 2:
		runall("support")
	else:
		print "OK, nothing"

def runall(suffix = "support", callmain = 0):
	names = os.listdir(os.curdir)
	names.sort()
	for name in names:
		if name in (os.curdir, os.pardir): continue
		if not os.path.isdir(name): continue
		modname = name + suffix
		fname = os.path.join(name, modname + '.py')
		print fname
		if os.path.isfile(fname):
			os.chdir(name)
			print "import", modname
			exec "import "+modname
			if callmain: eval(modname + ".main()")
			os.chdir(os.pardir)

if __name__ == '__main__':
	main()
