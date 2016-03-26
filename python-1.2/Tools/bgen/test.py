# This is an absolutely horrid piece of code.
# I wrote it to exercise the (mostly automatically generated) interfaces to the
# Mac Toolbox that I was in the midst of creating.
# It consists of a fairly complete Main loop -- it handles most of the stuff
# that every application should have:
# 
# - moving windows
# - resizing windows
# - hanling the zoombox
# - handling the close box
# - handling the apple menu (including starting desk acc's)
# - key events (including key repeat)
# - update events
# 
# It also detects clicks in controls and tracks the control.

from Evt import *
from Win import *
from Dlg import *
from Ctl import *
from Menu import *
from Qd import *
from Res import *
import AE

from addpack import addpack
addpack('Demo')
addpack('bgen')
addpack('evt')
addpack('win')
addpack('ctl')

from Events import *
from Windows import *
from Controls import *

import MacOS
MacOS.EnableAppswitch(0) # Stop Python from ever getting events itself

everywhere = (-32000, -32000, 32000, 32000)
# NB using 0x7fff doesn't work -- apparently a little slop must be present

print "There are now", len(dir()), "symbols in the name space!"

def main():
	appleid = 1
	ClearMenuBar()
	applemenu = NewMenu(appleid, "\024")
	applemenu.AppendMenu("All about me...;(-")
	applemenu.AddResMenu('DRVR')
	applemenu.InsertMenu(0)
	DrawMenuBar()
	
	winwidth = 200
	winheight = 100
	r = (30, 60, 30+winwidth, 60+winheight)
	w = NewWindow(r, "Hello world", 1, zoomDocProc, -1, 1, 0)
	resizerect = (10, 20, 70, 40)
	resize = NewControl(w, resizerect, "Resize", 1, 0, 0, 1, pushButProc, 0)
	quitrect = (90, 20, 130, 40)
	quit = NewControl(w, quitrect, "Quit", 1, 0, 0, 1, pushButProc, 0)
	while 1:
		doit, event = WaitNextEvent(-1,0)
		if doit:
			SetPort(w)
			(what, message, when, where, modifiers) = event
			if what == mouseDown:
				partcode, win = FindWindow(where)
				if partcode == inDrag: # transvestites, take note
					win.DragWindow(where, everywhere)
				elif partcode == inGoAway:
					if win.TrackGoAway(where):
						break
				elif partcode in (inZoomIn, inZoomOut):
					SetPort(win) # !!!
					if win.TrackBox(where, partcode):
						win.ZoomWindow(partcode, 1)
				elif partcode == inSysWindow:
					print "SystemWindow"
				elif partcode == inDesk:
					print "Desk"
				elif partcode == inMenuBar:
					result = MenuSelect(where)
					id = (result>>16) & 0xffff
					if id:
						item = result & 0xffff
						print "Menu id", id, ", item", item
						if id == appleid:
							name = applemenu.GetItem(item)
							print name
							OpenDeskAcc(name)
					HiliteMenu(0)
				elif partcode == inGrow:
					result = win.GrowWindow(where, everywhere)
					if result:
						winheight = (result>>16) & 0xffff
						winwidth = result & 0xffff
						win.SizeWindow(winwidth, winheight, 0)
						SetPort(win)
						InvalRect(everywhere)
				elif partcode == inContent:
					local = GlobalToLocal(where)
					print "local =", local
					ctltype, control = FindControl(local, win)
					if ctltype and control:
						pcode = control.TrackControl(local)
						if pcode:
							if control is resize:
								if winwidth == 200:
									winwidth = 300
								else:
									winwidth = 200
								win.SizeWindow(winwidth, winheight, 0)
								SetPort(win)
								InvalRect(everywhere)
							elif control is quit:
								break
					else:
						print ctltype, control
				else:
					print "Mouse down at", where, "(global)"
					print partcode, win
			elif what == mouseUp:
				print "Mouse up at", where, "(global)"
			elif what == keyDown:
				print "Key down:", hex(message), hex(modifiers)
				char = chr(message & 0xff)
				keycode = (message & 0xff00) >> 8
				print 'char:', `char`, '; keycode:', keycode
				if char == 'Q': break
			elif what == autoKey:
				print "Key repeat:", hex(message), hex(modifiers)
			elif what == updateEvt:
				print "update Event", message, modifiers
				w.BeginUpdate()
				EraseRect(everywhere)
				MoveTo(0, 0)
				LineTo(100, 100)
				TextSize(9)
				DrawString("This is a dead parrot!")
				MoveTo(0, 100)
				LineTo(100, 0)
				Move(0, 20)
				TextSize(12)
				DrawString("Nobody expects the Spanish Inquisition")
				TextSize(20)
				DrawString("!")
				UpdateControls(w)
				w.DrawGrowIcon()
				w.EndUpdate()
			elif what == activateEvt:
				print "activateEvt:", message, modifiers
				InitCursor()
			elif what == osEvt:
				print "osEvt:", message, where, modifiers
			elif what == 23:
				try:
					AE.AEProcessAppleEvent(event)
				except AE.Error, msg:
					print "AE.Error:", msg
			else:
				print "???", event

main()
