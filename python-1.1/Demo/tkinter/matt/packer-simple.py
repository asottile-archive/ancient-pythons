from Tkinter import *


class Test(Frame):
    def printit(self):
	print self.hi_there["command"]

    def createWidgets(self):
	# a hello button
	self.QUIT = Button(self, {'text': 'QUIT', 
				  'fg': 'red', 
				  'command': self.quit})
	
	self.QUIT.pack({'side': 'left', 'fill': 'both'})


	self.hi_there = Button(self, {'text': 'Hello', 
				      'command' : self.printit})
	self.hi_there.pack({'side': 'left'})

	# note how Packer defaults to {'side': 'top'}

	self.guy2 = Button(self, {'text': 'button 2'})
	self.guy2.pack()

	self.guy3 = Button(self, {'text': 'button 3'})
	self.guy3.pack()

    def __init__(self, master=None):
	Frame.__init__(self, master)
	Pack.config(self)
	self.createWidgets()

test = Test()
test.mainloop()
