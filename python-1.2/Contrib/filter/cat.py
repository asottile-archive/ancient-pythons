#!/usr/local/bin/python

# This very simple example passes it's commnad line arguments to the
# basic file_filter class and then runs the resulting "filter".

from filter import *

def main() :
	catter = file_filter(argv[1:])
	catter.run()

main()
