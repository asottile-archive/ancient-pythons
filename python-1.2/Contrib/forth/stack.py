#!/usr/Util/bin/python
#
# @(#)stack.py	1.2
#   
#   stack.py
#      generic stack class.

StackError = 'StackError'

class Stack:
    def __init__(self):
	self.__heap = []

    def push (self, word):
	self.__heap.append (word)
	
    def pop (self):
	if len(self.__heap) == 0:
	    raise StackError, "stack underflow"

	result = self.__heap[-1]
	del self.__heap[-1]
	return result

    def __repr__(self):
	return `self.__heap`
	
    def __str__(self):
	return `self.__heap`

    def flush (self):
	self.__heap = []
