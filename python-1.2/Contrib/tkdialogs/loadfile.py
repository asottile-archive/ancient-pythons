#! /usr/local/bin/python

import filedlg
from Tkinter import *

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)


        self.button = Button(self)
        self.button['text'] = 'Load File...'
        self.button['command'] = self.Press
        self.button.pack({"side": "top"})

        self.pack()

    def Press(self):
        fileDlg = filedlg.LoadFileDialog(app)
        if fileDlg.Show() != 1:
            fileDlg.DialogCleanup()
            return
        fname = fileDlg.GetFileName()
        self.button['text'] = 'File: ' + fname
        fileDlg.DialogCleanup()
    

app = Application()
app.mainloop()
