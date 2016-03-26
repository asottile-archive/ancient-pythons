# This is the file "wpy_phys.py".  It contains all the code which is
# highly dependent on the native OS GUI.  Your app should NOT import it.
# It is meant to be easily implemented in Tk, XVT, WinNT, and other GUIs.
# It is Copyright (C) 1994, but is freely distributable.  THERE ARE
# NO WARRANTIES AT ALL, USE AT YOUR OWN RISK.
# Comments to:  Jim Ahlstrom        jim@interet.com.
#
# All public symbols must begin with "wpyphys" for variables, and
# "WpyPhys" for functions and classes to avoid name conflicts in wpy.py.
# Most classes in wpy.py have a corresponding class in this file.  The classes
# defined here provide the OS-dependent window functions needed by wpy.py.
# See wpy.py for the class definitions.  The additional abstract classes are:
#   WpyPhysWidget, an abstract class, the parent of all widgets.
#   WpyPhysMenu, an abstract class, the parent of menu items.
#
# The App class has special methods.  Other objects have only these
# standard methods:
#   WpyPhysCreateWindow
#	Called only for windows.  Called to create the window and all children.
#   WpyPhysDestroyWindow
#	Called only for windows.  It destroys a window and all children.
#   WpyPhysChangeEnabled
#	Called when the enabled flag is changed.  For controls,
#	enable/disable the control.
#   WpyPhysChangeScroll
#	For control scroll bars, change the position of the slider.
#   WpyPhysChange[VH]Scroll
#	For window scroll bars, change the position of the slider.
#   WpyPhysChangeSize
#	Change the size and location of the object after it is created.
#   WpyPhysChangeTitle
#	Called to change the text on the object.  A change in size is not
#	implied, so new text size should be smaller than the old.
#   WpyPhysChangeVisible
#	Called when the visible flag is changed.  Make the object visible
#	or invisible.
#
# This layer must send events to the handlers in wpy.py and the app.  See
# functions with name WpyPhysHandle*.
#
# This version is based on Tk and uses "tkinter", a C interface to
# Tcl/Tk which is included as part of Python.
#/* tkintermodule.c -- Interface to libtk.a and libtcl.a.
#   Copyright (C) 1994 Steen Lumholt */

import tkinter
import sys, os, string
import wpy    # Needed for event classes and flags.

wpyphysVersion = "0.10"
wpyphysWindowSystem = "Tk"
wpyphysWindowVersion = "3.6"

wpyphysNoMainWindow = "No main window"

wpyphysTk = None	# Tk environment.
wpyphysMainWin = None	# Main window.
wpyphysSequence = 0	# Used to generate unique names.
wpyphysNamesToPhys = {}	# Dictionary to translate names to class instances.
			# Some names are deliberately omitted.
wpyphysCanvasBd = 2	# Size of canvas border in pixels.
wpyphysCanvasRelief = "raised"	# Relief (style) of canvas border.

# Masks for the "state" field of an X event.
_wpyphysStateShift	= 1
_wpyphysStateControl	= 4

class WpyphysDummy:
  def meth(x):
    pass
wpyphyse = WpyphysDummy()
wpyphysTypeMeth = type(wpyphyse.meth)
del wpyphyse
del WpyphysDummy

def WpyPhysTkerror(err):
# Do not display dialog box for Tk background errors.
  pass

def WpyPhysExit(code="0"):
# Call Python exit instead Tk exit.
  import sys
  sys.exit(WpyPhysGetint(code))

def WpyPhysHandleChar(tkname, keyname, keynum, keyascii, state):
  try:
    self = wpyphysNamesToPhys[tkname]
  except KeyError:
    return
  keynum = string.atoi(keynum)
  if keynum >= 32 and keynum <= 127:
    pass
  elif keyname == "Return":
    if self.wpyDefaultButton != None:
      WpyPhysHandleButton(self.wpyDefaultButton.wpyphysTkName)
      return
    keynum = 13
    keyascii = "\r"
  else:
    return
  event = wpy.WpyEvent()
  event.wpyKeyNum = keynum
  event.wpyKeyASCII = keyascii
  # Generate appropriate call for function or method.
  if type(self.WpyOnChar) == wpyphysTypeMeth:
    self.WpyOnChar(event)
  else:
    self.WpyOnChar(self, event)

def WpyPhysHandleButton(tkname):
# Handle button press events.
  try:
    self = wpyphysNamesToPhys[tkname]
  except KeyError:
    return
  event = wpy.WpyEvent()
  if self.__dict__.has_key("wpyPhysIvar"):
    self.wpyButtonValue = string.atoi(wpyphysTk.globalgetvar(self.wpyPhysIvar))
  elif self.__dict__.has_key("wpyPhysVarName"):
    self.wpyGroup.wpyButtonValue = wpyphysNamesToPhys[
          wpyphysTk.globalgetvar(self.wpyPhysVarName)]
  # Generate appropriate call for function or method.
  if type(self.WpyOnButton) == wpyphysTypeMeth:
    self.WpyOnButton(event)
  else:
    self.WpyOnButton(self, event)

def WpyPhysHandleClose(tkname):
  try:
    self = wpyphysNamesToPhys[tkname]
  except KeyError:
    return
  event = wpy.WpyEvent()
  # Generate appropriate call for function or method.
  if type(self.WpyOnClose) == wpyphysTypeMeth:
    self.WpyOnClose(event)
  else:
    self.WpyOnClose(self, event)

def WpyPhysHandleFocus(tkname, focusin, detail):
  try:
    self = wpyphysNamesToPhys[tkname]
  except KeyError:
    return
  if detail == "NotifyVirtual":
    event = wpy.WpyEvent()
    event.wpyFocusIn = string.atoi(focusin)
    # Generate appropriate call for function or method.
    if type(self.WpyOnFocus) == wpyphysTypeMeth:
      self.WpyOnFocus(event)
    else:
      self.WpyOnFocus(self, event)

def WpyPhysHandleMouse(tkname, eventtype, button, locx, locy, state):
# Handle mouse events.  These can only be sent to a toplevel or
# child window, not to a dialog.
  try:
    self = wpyphysNamesToPhys[tkname]
  except KeyError:
    return
  x   = string.atoi(locx)
  y   = string.atoi(locy)
  while not self.wpyFlags & wpy.wpyFlagsWindow:	# Find the window
    if self.wpyParent == None:		# We are up to "App".
      return
    x = x + self.wpyLocX	# Convert to parent coordinates.
    y = y + self.wpyLocY
    self = self.wpyParent
  if self.wpyFlags & wpy.wpyFlagsDialog:	# No mouse for dialog.
    return
  event = wpy.WpyEvent()
  event.wpyType   = eventtype
  state = string.atoi(state)
  event.wpyPressed = state >> 8
  event.wpyButton = string.atoi(button)
  event.wpyLocX   = x
  event.wpyLocY   = y
  event.wpyShift   = state & _wpyphysStateShift
  event.wpyControl = state & _wpyphysStateControl
  # Generate appropriate call for function or method.
  if type(self.WpyOnMouse) == wpyphysTypeMeth:
    self.WpyOnMouse(event)
  else:
    self.WpyOnMouse(self, event)

def WpyPhysHandleConfigure(tkname, x, y, w, h, send):
# Handle Configure events.  These happen on resize or window move.
# Only used for toplevel windows since the user can not resize child windows.
# Only the size is used, so we can generate a size event on a resize by the user.
# NOTE: Window location is invalid (unless "send" is "1" ???).
  self = wpyphysNamesToPhys[tkname]
  self.wpyLocX = string.atoi(x)
  self.wpyLocY = string.atoi(y)
  if self.wpyphysTopSizeX < 0:
    return
  w = string.atoi(w)
  h = string.atoi(h)
  if not self.wpyHasResize:
    self.wpyphysTopSizeX = w
    self.wpyphysTopSizeY = h
    wpyphysTk.call("wm", "geometry", self.wpyphysTopName, "")
  elif (self.wpyphysTopSizeX != w) or (self.wpyphysTopSizeY != h):
    event = wpy.WpyEvent()
    event.wpyNewSizeX = w
    event.wpyNewSizeY = h
    event.wpyOldSizeX = self.wpyphysTopSizeX
    event.wpyOldSizeY = self.wpyphysTopSizeY
    event.wpyChangeSizeX = w - event.wpyOldSizeX
    event.wpyChangeSizeY = h - event.wpyOldSizeY
    print "New resize", self, w, h
    self.wpyphysTopSizeX = w
    self.wpyphysTopSizeY = h
    self.WpySendSizeEvent(event)

def WpyPhysHandleScroll(tkname, pos):
  self = wpyphysNamesToPhys[tkname]
  pos = string.atoi(pos)
  t = self.wpyScrollSize - self.wpyScrollWinSize
  if pos > t:
    pos = t
  if pos < 0:
    pos = 0
  event = wpy.WpyEvent()
  event.wpyScrollPos = pos
  # Generate appropriate call for function or method.
  if type(self.WpyOnScroll) == wpyphysTypeMeth:
    self.WpyOnScroll(event)
  else:
    self.WpyOnScroll(self, event)

def WpyPhysHandleVScroll(tkname, pos):
  self = wpyphysNamesToPhys[tkname]
  pos = string.atoi(pos)
  t = self.wpyVScrollSize - self.wpyVScrollWinSize
  if pos > t:
    pos = t
  if pos < 0:
    pos = 0
  event = wpy.WpyEvent()
  event.wpyScrollPos = pos
  # Generate appropriate call for function or method.
  if type(self.WpyOnVScroll) == wpyphysTypeMeth:
    self.WpyOnVScroll(event)
  else:
    self.WpyOnVScroll(self, event)

def WpyPhysHandleHScroll(tkname, pos):
  self = wpyphysNamesToPhys[tkname]
  pos = string.atoi(pos)
  t = self.wpyHScrollSize - self.wpyHScrollWinSize
  if pos > t:
    pos = t
  if pos < 0:
    pos = 0
  event = wpy.WpyEvent()
  event.wpyScrollPos = pos
  # Generate appropriate call for function or method.
  if type(self.WpyOnHScroll) == wpyphysTypeMeth:
    self.WpyOnHScroll(event)
  else:
    self.WpyOnHScroll(self, event)

def WpyPhysGetint(s):
# Convert string to int.
  return wpyphysTk.getint(s)

def WpyPhysGetdouble(s):
# Convert string to double.
  return wpyphysTk.getdouble(s)

def WpyPhysGetboolean(s):
# Convert string to boolean.
  return wpyphysTk.getboolean(s)

class WpyPhysApp:
  def WpyPhysAppInit(self):
  # Called when user gets an WpyApp instance.  Only one WpyApp instance allowed.
    global wpyphysTk
    self.wpyphysTkName = "app"
    wpyphysNamesToPhys["app"] = self
    self.wpyphysBaseName = os.path.basename(sys.argv[0])
    if self.wpyphysBaseName[-3:] == ".py":
      self.wpyphysBaseName = self.wpyphysBaseName[:-3]
    wpyphysTk = tkinter.create(None, self.wpyphysBaseName, "Tk", 0)
    self.wpyphysTk = wpyphysTk
    wpyphysTk.createcommand("tkerror", WpyPhysTkerror)
    wpyphysTk.createcommand("exit", WpyPhysExit)
    wpyphysTk.createcommand("HandleButton",	WpyPhysHandleButton)
    wpyphysTk.createcommand("HandleChar",	WpyPhysHandleChar)
    wpyphysTk.createcommand("HandleClose",	WpyPhysHandleClose)
    wpyphysTk.createcommand("HandleConfigure",	WpyPhysHandleConfigure)
    wpyphysTk.createcommand("HandleFocus",	WpyPhysHandleFocus)
    wpyphysTk.createcommand("HandleMouse",	WpyPhysHandleMouse)
    wpyphysTk.createcommand("HandleScroll",	WpyPhysHandleScroll)
    wpyphysTk.createcommand("HandleVScroll",	WpyPhysHandleVScroll)
    wpyphysTk.createcommand("HandleHScroll",	WpyPhysHandleHScroll)
    # Try to read in a Tk option file.
    for dir in sys.path:
      try:
        file = os.path.join(dir, "wpy_tk.dfl")
        fd = open(file, "r")
        fd.close()
        wpyphysTk.call("option", "readfile", file)
      except IOError:
        pass
    # Exit if user hits Control-C.
    t = ("exit", "3")
    wpyphysTk.call("bind", "all", "<Control-c>", t)
    t = ("HandleChar", "%W", "%K", "%N", "%A", "%s")
    wpyphysTk.call("bind", "all", "<Key>", t)
    t = ("HandleMouse", "%W", "p", "%b", "%x", "%y", "%s")
    wpyphysTk.call("bind", "all", "<Any-ButtonPress>", t)
    t = ("HandleMouse", "%W", "r", "%b", "%x", "%y", "%s")
    wpyphysTk.call("bind", "all", "<Any-ButtonRelease>", t)
    t = ("HandleMouse", "%W", "d", "%b", "%x", "%y", "%s")
    wpyphysTk.call("bind", "all", "<Any-Double-Button>", t)
    t = ("HandleFocus", "%W", "1", "%d")
    wpyphysTk.call("bind", "all", "<FocusIn>", t)
    t = ("HandleFocus", "%W", "0", "%d")
    wpyphysTk.call("bind", "all", "<FocusOut>", t)
    # WpyApp is not a visible object.  The name "." will be assigned
    #   to the first top-level window created.
    wpyphysTk.call("wm", "withdraw", ".")
    # Get some control and text metrics.
    wpyphysTk.call("label", ".m10", "-text", "mmmmmmmmmm", "-bd", "0")
    self.wpyCharSizeX  = string.atoi(wpyphysTk.call(
                "winfo", "reqwidth", ".m10")) / 10
    self.wpyCharSizeY = string.atoi(wpyphysTk.call(
                "winfo", "reqheight", ".m10"))
    wpyphysTk.call("destroy", ".m10")
    global wpyphysCanvasBd
    global wpyphysCanvasRelief
    wpyphysTk.call("canvas", ".c1")
    wpyphysCanvasBd  = string.split(
              wpyphysTk.call(".c1", "configure", "-bd"))[4]
    wpyphysCanvasBd  = string.atoi(wpyphysCanvasBd)
    wpyphysCanvasRelief = string.split(
              wpyphysTk.call(".c1", "configure", "-relief"))[4]
    wpyphysTk.call("destroy", ".c1")
    # Get screen size, WpyApp has the size of the screen.
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0
    t = wpyphysTk.call("winfo", "screenheight", ".")
    self.wpySizeY = string.atoi(t)
    t = wpyphysTk.call("winfo", "screenwidth", ".")
    self.wpySizeX = string.atoi(t)
    self.wpyLocX = self.wpyLocY = 0
    t = wpyphysTk.call("winfo", "pixels", ".", "100c")
    self.wpyOneMeter = string.atoi(t)
  def WpyPhysMainLoop(self):
  # Main event loop: wait for and react to events.
    wpyphysTk.mainloop()

class WpyPhysWidget:
# Abstract class.
  def WpyPhysNewName(self, name = None):
    global wpyphysSequence
    global wpyphysNamesToPhys
    wpyphysSequence = wpyphysSequence + 1
    if name == None:
      name = self.wpyParent.wpyphysTkName	# parent name
    if name == "app":
      name = ".obj%d" % wpyphysSequence
    elif name == ".":
      name = ".obj%d" % wpyphysSequence
    else:
      name = name + ".obj%d" % wpyphysSequence
    self.wpyphysTkName = name
    wpyphysNamesToPhys[name] = self
    return name
  def WpyPhysPrivatePass1(self):
  # Pass1 is called top down, i.e. parents before children for all objects
  # exactly once.  Used to create sizes of objects which depend on options
  # which may have been reset by the user.
    self.WpyPhysCreatePass1()
    for object in self.wpyChildList:
      object.WpyPhysPrivatePass1()
  def WpyPhysPrivatePass2(self):
  # Pass2 is called for all objects after all Pass1 calls.  Create the object.
  # All non-window objects are called first, then windows.
  # This is meant to provide an opportunity for final display.
    if self.wpyFlags & wpy.wpyFlagsWindow:
      self.WpyOnCreate(None)
      if type(self.WpyOnSize) == wpy.wpyTypeMeth:
        self.WpyOnSize(None)
      else:
        self.WpyOnSize(self, None)
    self.WpyPhysCreatePass2()
    self.wpyCreated = 1
    for obj in self.wpyChildList:
      obj.WpyPhysPrivatePass2()
  def WpyPhysCreatePass1(self):
    pass
  def WpyPhysChangeSize(self):
    if self.wpyVisible:
      wpyphysTk.call("place", self.wpyphysTkName,
           "-x", int(self.wpyLocX), "-y", int(self.wpyLocY),
           "-width", int(self.wpySizeX), "-height", int(self.wpySizeY))
  def WpyPhysChangeVisible(self, visible):
    if visible:
      wpyphysTk.call("place", self.wpyphysTkName,
         "-x", int(self.wpyLocX), "-y", int(self.wpyLocY),
         "-width", int(self.wpySizeX), "-height", int(self.wpySizeY))
    else:
      wpyphysTk.call("place", "forget", self.wpyphysTkName)
  def WpyPhysChangeTitle(self, title):
    wpyphysTk.call(self.wpyphysTkName, "configure", "-text", title)

# Start of menus.

class WpyPhysMenu(WpyPhysWidget):
# An abstract class.
  def WpyPhysChangeEnabled(self, enabled):
    index = self.wpyParent.wpyMenuItems.index(self)
    menu = self.wpyParent.menuName
    if enabled:
      wpyphysTk.call(menu, "entryconfigure", index, "-state", "normal")
    else:
      wpyphysTk.call(menu, "entryconfigure", index, "-state", "disabled")
  def WpyPhysChangeTitle(self, title):
    index = self.wpyParent.wpyMenuItems.index(self)
    menu = self.wpyParent.menuName
    wpyphysTk.call(menu, "entryconfigure", index, "-label", title)
  def WpyPhysChangeSize(self):
    pass
  def WpyPhysChangeVisible(self, visible):
    pass

class WpyPhysMenuBar(WpyPhysWidget):
  def WpyPhysCreatePass2(self):
    tup = ("tk_menuBar", self.wpyphysTkName)
    for item in self.wpyMenuItems:
      buttonname = item.wpyphysTkName
      tup = tup + (buttonname,)
      wpyphysTk.call("menubutton", buttonname, "-text", item.wpyTitle,
           "-menu", item.menuName)
      wpyphysTk.call("pack", buttonname, "-side", "left")
    apply(wpyphysTk.call, tup)
  def WpyPhysChangeEnabled(self, enabled):
    pass
  def WpyPhysChangeSize(self):
    pass
  def WpyPhysChangeTitle(self, title):
    pass
  def WpyPhysChangeVisible(self, visible):
    pass

class WpyPhysBarPopup(WpyPhysWidget):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    self.menuName = name + ".menu%d" % wpyphysSequence
  def WpyPhysCreatePass2(self):
    wpyphysTk.call("menu", self.menuName)
    self.WpyPhysChangeEnabled(self.wpyEnabled)
  def WpyPhysChangeEnabled(self, enabled):
    if enabled:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-state", "normal")
    else:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-state", "disabled")
  def WpyPhysChangeSize(self):
    pass
  def WpyPhysChangeTitle(self, title):
    wpyphysTk.call(self.wpyphysTkName, "configure", "-text", title)
  def WpyPhysChangeVisible(self, visible):
    pass

class WpyPhysTopPopup(WpyPhysWidget):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    self.menuName = name
  def WpyPhysCreatePass2(self):
    wpyphysTk.call("menu", self.wpyphysTkName)
  def WpyPhysChangeEnabled(self, enabled):
    pass
  def WpyPhysChangeSize(self):
    pass
  def WpyPhysChangeTitle(self, title):
    pass
  def WpyPhysChangeVisible(self, visible):
    if visible:
      x = wpyphysTk.call("winfo", "rootx", self.wpyParent.wpyphysTkName)
      y = wpyphysTk.call("winfo", "rooty", self.wpyParent.wpyphysTkName)
      x = string.atoi(x)
      y = string.atoi(y)
      x = x + self.wpyLocX	# BUG
      y = y + self.wpyLocY
      wpyphysTk.call(self.wpyphysTkName, "post", int(x), int(y))
    else:
      wpyphysTk.call(self.wpyphysTkName, "unpost")

# Start of menu items.

class WpyPhysMenuButton(WpyPhysMenu):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    self.wpyParentMenuName = self.wpyParent.menuName
  def WpyPhysCreatePass2(self):
    t = ("HandleButton", self.wpyphysTkName)
    wpyphysTk.call(self.wpyParentMenuName, "add", "command",
        "-label", self.wpyTitle, "-command", t)
    self.WpyPhysChangeEnabled(self.wpyEnabled)

class WpyPhysMenuCheck(WpyPhysMenu):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    self.wpyParentMenuName = self.wpyParent.menuName
    self.wpyPhysIvar = "gvar%d" % wpyphysSequence
  def WpyPhysCreatePass2(self):
    var = self.wpyPhysIvar
    t = ("HandleButton", self.wpyphysTkName)
    wpyphysTk.call(self.wpyParentMenuName, "add", "checkbutton",
        "-label", self.wpyTitle, "-variable", var, "-command", t)
    if self.wpyButtonValue:
      wpyphysTk.globalsetvar(var, "1")
    else:
      wpyphysTk.globalsetvar(var, "0")
    self.WpyPhysChangeEnabled(self.wpyEnabled)

class WpyPhysMenuLine(WpyPhysMenu):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    self.wpyParentMenuName = self.wpyParent.menuName
  def WpyPhysCreatePass2(self):
    wpyphysTk.call(self.wpyParentMenuName, "add", "separator")
  def WpyPhysChangeEnabled(self, enabled):
    pass
  def WpyPhysChangeTitle(self, title):
    pass

class WpyPhysMenuPopup(WpyPhysMenu):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    self.wpyParentMenuName = self.wpyParent.menuName
    self.menuName = self.wpyParentMenuName + ".menu%d" % wpyphysSequence
  def WpyPhysCreatePass2(self):
    wpyphysTk.call(self.wpyParentMenuName, "add", "cascade",
        "-label", self.wpyTitle, "-menu", self.menuName)
    wpyphysTk.call("menu", self.menuName)
    self.WpyPhysChangeEnabled(self.wpyEnabled)

class WpyPhysMenuRadio(WpyPhysMenu):
  def WpyPhysCreatePass1(self):
    self.wpyParentMenuName = self.wpyGroup.wpyParent.menuName
    name = self.WpyPhysNewName()
    if self.wpyGroup == self:	# Start of new group
      self.wpyPhysVarName = "gvar%d" % wpyphysSequence
    else:			# Copy the group variable name
      self.wpyPhysVarName = self.wpyGroup.wpyPhysVarName
  def WpyPhysCreatePass2(self):
    var = self.wpyPhysVarName
    t = ("HandleButton", self.wpyphysTkName)
    wpyphysTk.call(self.wpyParentMenuName, "add", "radiobutton",
        "-label", self.wpyTitle,
        "-variable", var, "-value", self.wpyphysTkName, "-command", t)
    if self.wpyGroup.wpyButtonValue.wpyphysTkName == self.wpyphysTkName:
      wpyphysTk.globalsetvar(var, self.wpyphysTkName)
    self.WpyPhysChangeEnabled(self.wpyEnabled)

# End of menus.

#start of controls.

class WpyPhysBox:
  def WpyPhysCreatePass1(self):
    self.wpyphysItem = None
  def WpyPhysCreatePass2(self):
    self.WpyPhysChangeVisible(self.wpyVisible)
  def WpyPhysChangeSize(self):
    self.WpyPhysChangeVisible(self.wpyVisible)
  def WpyPhysChangeVisible(self, visible):
    if self.wpyphysItem != None:
      wpyphysTk.call(self.wpyphysTkName, "delete", self.wpyphysItem)
      self.wpyphysItem = None
    if visible:
      i1 = self.wpyFrameSizeX / 2
      i2 = (self.wpyFrameSizeX + 1) / 2 - 1
      self.wpyphysItem = wpyphysTk.call(self.wpyphysTkName,
            "create", "rectangle",
            self.wpyLocX + i1, self.wpyLocY + i1,
            self.wpyLocX + self.wpySizeX + i2,
            self.wpyLocY + self.wpySizeY + i2,
            "-width", self.wpyFrameSizeX)

class WpyPhysButton(WpyPhysWidget):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    t = ("HandleButton", name)
    wpyphysTk.call("button", name,"-text", self.wpyTitle, "-command", t)
    self.wpyphysMyRect = None
    self.wpyphysRectSize = 0
    # Must set up initial sizes and units.
    self.wpySizeX = string.atoi(wpyphysTk.call("winfo", "reqwidth", name))
    self.wpySizeY = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0
  def WpyPhysCreatePass2(self):
    wpyphysTk.call(self.wpyphysTkName, "configure", "-text", self.wpyTitle)
    self.WpyPhysChangeSize()
    self.WpyPhysChangeEnabled(self.wpyEnabled)
    self.WpyPhysChangeVisible(self.wpyVisible)
    if self.wpyParent.wpyDefaultButton == self:
      self.wpyphysRectSize = 3
      self.WpyPhysDrawRect()
  def WpyPhysChangeEnabled(self, enabled):
    if enabled:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-state", "normal")
    else:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-state", "disabled")
  def WpyPhysChangeSize(self):
    WpyPhysWidget.WpyPhysChangeSize(self)
    if self.wpyphysRectSize:
      self.WpyPhysDrawRect()
  def WpyPhysChangeVisible(self, visible):
    WpyPhysWidget.WpyPhysChangeVisible(self, visible)
    if self.wpyphysRectSize:
      self.WpyPhysDrawRect()
  def WpyPhysDrawRect(self):
    canvas = self.wpyParent.wpyphysTkName
    if self.wpyphysMyRect != None:
      wpyphysTk.call(canvas, "delete", self.wpyphysMyRect)
      self.wpyphysMyRect = None
    if self.wpyVisible:
      i1 = (self.wpyphysRectSize + 1) / 2
      self.wpyphysMyRect = wpyphysTk.call(canvas, "create", "rectangle",
            self.wpyLocX - i1, self.wpyLocY - i1,
            self.wpyLocX + self.wpySizeX + i1,
            self.wpyLocY + self.wpySizeY + i1,
            "-width", self.wpyphysRectSize)

class WpyPhysCheckButton(WpyPhysWidget):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    self.wpyPhysIvar = "gvar%d" % wpyphysSequence
    t = ("HandleButton", name)
    wpyphysTk.call("checkbutton", name,"-text", self.wpyTitle,
       "-command", t, "-variable", self.wpyPhysIvar)
    # Must set up initial sizes and units.
    #wpyphysTk.call("place", name, "-x", "0", "-y", "0")
    #wpyphysTk.call("update", "idletasks")
    self.wpySizeX = string.atoi(wpyphysTk.call("winfo", "reqwidth", name))
    self.wpySizeY = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0
  def WpyPhysCreatePass2(self):
    wpyphysTk.call(self.wpyphysTkName, "configure", "-text", self.wpyTitle)
    if self.wpyButtonValue:
      wpyphysTk.globalsetvar(self.wpyPhysIvar, "1")
    else:
      wpyphysTk.globalsetvar(self.wpyPhysIvar, "0")
    self.WpyPhysChangeSize()
    self.WpyPhysChangeEnabled(self.wpyEnabled)
    self.WpyPhysChangeVisible(self.wpyVisible)
  def WpyPhysChangeEnabled(self, enabled):
    if enabled:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-state", "normal")
    else:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-state", "disabled")

class WpyPhysLabel(WpyPhysWidget):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    wpyphysTk.call("label", name, "-text", self.wpyTitle)
    # Must set up initial sizes and units.
    self.wpySizeX = string.atoi(wpyphysTk.call("winfo", "reqwidth", name))
    self.wpySizeY = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0
  def WpyPhysCreatePass2(self):
    wpyphysTk.call(self.wpyphysTkName, "configure", "-text", self.wpyTitle)
    t = self.wpyAnchor
    if len(t) != 1:
      t = t[1]
    if t == "w":
      wpyphysTk.call(self.wpyphysTkName, "configure", "-anchor", "w")
    elif t == "e":
      wpyphysTk.call(self.wpyphysTkName, "configure", "-anchor", "e")
    else:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-anchor", "center")
    self.WpyPhysChangeSize()

class WpyPhysMessage(WpyPhysWidget):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    a = `int(self.aspect * 100 + 0.5)`
    wpyphysTk.call("message", name, "-text", self.wpyTitle,
         "-aspect", a, "-justify", self.justify)
    # Must set up initial sizes and units.
    self.wpySizeX = string.atoi(wpyphysTk.call("winfo", "reqwidth", name))
    self.wpySizeY = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0
  def WpyPhysCreatePass2(self):
    wpyphysTk.call(self.wpyphysTkName, "configure", "-text", self.wpyTitle)
    self.WpyPhysChangeSize()

class WpyPhysRadioButton(WpyPhysWidget):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    if self.wpyGroup == self:	# Start of new group
      self.wpyPhysVarName = "gvar%d" % wpyphysSequence
    else:			# Copy the group variable name
      self.wpyPhysVarName = self.wpyGroup.wpyPhysVarName
    t = ("HandleButton", name)
    wpyphysTk.call("radiobutton", name,"-text", self.wpyTitle,
       "-command", t, "-variable", self.wpyPhysVarName, "-value", name)
    # Must set up initial sizes and units.
    self.wpySizeX = string.atoi(wpyphysTk.call("winfo", "reqwidth", name))
    self.wpySizeY = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0
  def WpyPhysCreatePass2(self):
    wpyphysTk.call(self.wpyphysTkName, "configure", "-text", self.wpyTitle)
    if self.wpyGroup.wpyButtonValue.wpyphysTkName == self.wpyphysTkName:
      wpyphysTk.globalsetvar(self.wpyPhysVarName, self.wpyphysTkName)
    self.WpyPhysChangeSize()
    self.WpyPhysChangeEnabled(self.wpyEnabled)
    self.WpyPhysChangeVisible(self.wpyVisible)
  def WpyPhysChangeEnabled(self, enabled):
    if enabled:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-state", "normal")
    else:
      wpyphysTk.call(self.wpyphysTkName, "configure", "-state", "disabled")

class WpyPhysScroll(WpyPhysWidget):
  def WpyPhysCreatePass1(self):
    name = self.WpyPhysNewName()
    t = ("HandleScroll", name)
    if self.wpyTitle[0] == "h":
      wpyphysTk.call("scrollbar", name, "-command", t, "-orient", "horizontal")
      self.wpySizeY = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
      self.wpySizeX = 0
      self.wpyFrameSizeX = self.wpyFrameSizeY = 0
    else:
      wpyphysTk.call("scrollbar", name, "-command", t)
      self.wpySizeX = string.atoi(wpyphysTk.call("winfo", "reqwidth", name))
      self.wpySizeY = 0
      self.wpyFrameSizeX = self.wpyFrameSizeY = 0
  def WpyPhysCreatePass2(self):
    self.WpyPhysChangeSize()
    self.WpyPhysChangeScroll(self.wpyScrollPos)
  def WpyPhysChangeScroll(self, pos):
    if self.wpyScrollSize <= self.wpyScrollWinSize:
      wpyphysTk.call(self.wpyphysTkName, "set", "1", "1", "0", "0")
    else:
      wpyphysTk.call(self.wpyphysTkName, "set",
        self.wpyScrollSize, self.wpyScrollWinSize, pos,
        pos + self.wpyScrollWinSize - 1)
  def WpyPhysChangeEnabled(self, enabled):
    pass
  def WpyPhysChangeVisible(self, visible):
    pass
  def WpyPhysChangeTitle(self, title):
    pass

# End of controls.

# Start of windows.

class WpyPhysDialog(WpyPhysWidget):
  def WpyPhysCreateWindow(self):
    self.WpyPhysPrivatePass1()
    self.WpyPhysPrivatePass2()
  def WpyPhysCreatePass1(self):
    global wpyphysSequence
    global wpyphysNamesToPhys
    wpyphysSequence = wpyphysSequence + 1
    name = ".obj%d" % wpyphysSequence
    self.wpyphysTopName = name
    wpyphysNamesToPhys[name] = self
    wpyphysTk.call("toplevel", name)
    wpyphysTk.call("wm", "withdraw", name)
    t = ("HandleClose", name)
    wpyphysTk.call("wm", "protocol", name, "WM_DELETE_WINDOW", t)
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0
    wpyphysSequence = wpyphysSequence + 1
    name = name + ".obj%d" % wpyphysSequence
    self.wpyphysTkName = name
    wpyphysTk.call("canvas", name)
    wpyphysNamesToPhys[name] = self
  def WpyPhysCreatePass2(self):
    wpyphysTk.call("wm", "title", self.wpyphysTopName, self.wpyTitle)
    wpyphysTk.call(self.wpyphysTkName, "configure",
         "-width", self.wpySizeX, "-height", self.wpySizeY)
    wpyphysTk.call("pack", self.wpyphysTkName, "-in", self.wpyphysTopName,
          "-expand", "1", "-fill", "both")
    wpyphysTk.call("focus", self.wpyphysTopName)
    WpyPhysDialog.WpyPhysChangeVisible(self, self.wpyVisible)
  def WpyPhysDestroyWindow(self):
    wpyphysTk.call("destroy", self.wpyphysTopName)
  def WpyPhysChangeSize(self):
    wpyphysTk.call(self.wpyphysTkName, "configure",
         "-width", self.wpySizeX, "-height", self.wpySizeY)
    wpyphysTk.call("wm", "geometry", self.wpyphysTopName, "")
  def WpyPhysChangeTitle(self, title):
    wpyphysTk.call("wm", "title", self.wpyphysTopName, title)
  def WpyPhysChangeVisible(self, visible):
    if visible:
      wpyphysTk.call("wm", "deiconify", self.wpyphysTopName)
    else:
      wpyphysTk.call("wm", "withdraw", self.wpyphysTopName)

class WpyPhysModalDialog(WpyPhysWidget):
# Note: Change to "visible" is ignored.
  def WpyPhysCreateWindow(self):
    self.WpyPhysPrivatePass1()
    self.WpyPhysPrivatePass2()
    # This will not return until the user destroys the window.
    # Make sure there is a way to do that !!!
    oldFocus = wpyphysTk.call("focus")
    wpyphysTk.call("wm", "deiconify", self.wpyphysTopName)
    wpyphysTk.call("focus", self.wpyphysTopName)
    wpyphysTk.call("grab", "set", self.wpyphysTopName)
    wpyphysTk.call("tkwait", "window", self.wpyphysTopName)
    wpyphysTk.call("focus", oldFocus)
  def WpyPhysCreatePass1(self):
    global wpyphysSequence
    global wpyphysNamesToPhys
    wpyphysSequence = wpyphysSequence + 1
    name = ".obj%d" % wpyphysSequence
    self.wpyphysTopName = name
    wpyphysNamesToPhys[name] = self
    wpyphysTk.call("toplevel", name)
    wpyphysTk.call("wm", "withdraw", name)
    t = ("HandleClose", name)
    wpyphysTk.call("wm", "protocol", name, "WM_DELETE_WINDOW", t)
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0
    wpyphysSequence = wpyphysSequence + 1
    name = name + ".obj%d" % wpyphysSequence
    self.wpyphysTkName = name
    wpyphysTk.call("canvas", name)
    wpyphysNamesToPhys[name] = self
  def WpyPhysCreatePass2(self):
    wpyphysTk.call("wm", "title", self.wpyphysTopName, self.wpyTitle)
    wpyphysTk.call(self.wpyphysTkName, "configure",
         "-width", self.wpySizeX, "-height", self.wpySizeY)
    wpyphysTk.call("pack", self.wpyphysTkName, "-in", self.wpyphysTopName,
          "-expand", "1", "-fill", "both")
  def WpyPhysDestroyWindow(self):
    wpyphysTk.call("destroy", self.wpyphysTopName)
  def WpyPhysChangeSize(self):
    wpyphysTk.call(self.wpyphysTkName, "configure",
         "-width", self.wpySizeX, "-height", self.wpySizeY)
    wpyphysTk.call("wm", "geometry", self.wpyphysTopName, "")
  def WpyPhysChangeTitle(self, title):
    wpyphysTk.call("wm", "title", self.wpyphysTopName, title)

class WpyPhysWindow(WpyPhysWidget):
  def WpyWriteText(self, x, y, anchor, text):
    x = (self.wpyphysTkName, "create", "text", x, y,
          "-text", text, "-anchor", anchor)
    apply(wpyphysTk.call, x)
    self.wpyphysWrItems.append(x)
  def WpyWriteClear(self):
    wpyphysTk.call(self.wpyphysTkName, "delete", "all")
    self.wpyphysWrItems = []
  def WpyWriteRect(self, x1, y1, x2, y2, bd):
    wpyphysTk.call(self.wpyphysTkName, "create", "rectangle", x1, y1,
          x2, y2, "-width", bd)

class WpyPhysTopLevel(WpyPhysWindow):
# The main window is the first top-level window.
# Note: wpyphysTkName refers to the canvas, while wpyphysTopName
# is the container window.
  def WpyPhysCreateWindow(self):
    self.WpyPhysPrivatePass1()
    self.WpyPhysPrivatePass2()
    wpyphysTk.call("update")
    self.wpyphysTopSizeX = string.atoi(
          wpyphysTk.call("winfo", "width",  self.wpyphysTopName))
    self.wpyphysTopSizeY = string.atoi(
          wpyphysTk.call("winfo", "height", self.wpyphysTopName))
    wpyphysTk.call("focus", self.wpyphysTopName)
    t = ("HandleConfigure", "%W", "%x", "%y", "%w", "%h", "%E")
    wpyphysTk.call("bind", self.wpyphysTopName, "<Configure>", t)
  def WpyPhysCreatePass1(self):
    global wpyphysSequence
    global wpyphysNamesToPhys
    if wpyphysMainWin == None:
      wpyphysMainWin == self
      topname = "."
      frame = ".cframe"
      canvas = frame + ".canvas"
    else:
      wpyphysSequence = wpyphysSequence + 1
      topname = ".obj%d" % wpyphysSequence
      wpyphysTk.call("toplevel", topname)
      frame = topname + ".cframe"
      canvas = frame + ".canvas"
    self.wpyphysTkName = canvas
    self.wpyphysFrameName = frame
    self.wpyphysTopName = topname
    wpyphysNamesToPhys[topname] = self
    wpyphysNamesToPhys[canvas] = self
    wpyphysTk.call("wm", "withdraw", topname)
    t = ("HandleClose", topname)
    wpyphysTk.call("wm", "protocol", topname, "WM_DELETE_WINDOW", t)
    self.wpyFrameSizeX = self.wpyFrameSizeY = 0		# Not used.
    self.wpyphysTopSizeX = -1
    wpyphysTk.call("frame", frame, "-bd", wpyphysCanvasBd,
           "-relief", wpyphysCanvasRelief)
    wpyphysTk.call("canvas", canvas, "-bd", "0")
  #def WpyPhysCreatePass1(self):
    if self.wpyHasResize:
      wpyphysTk.call("wm", "minsize", self.wpyphysTopName, 1, 1)
    wpyphysTk.call("wm", "title", self.wpyphysTopName, self.wpyTitle)
    obj = self.wpyMenuBar
    if obj != None:
      menu = self.wpyphysTopName
      if menu == ".":
        menu = ".menu"
      else:
        menu = menu + ".menu"
      obj.wpyphysTkName = menu
      wpyphysTk.call("frame", menu, "-relief", wpyphysCanvasRelief,
             "-bd", wpyphysCanvasBd)
      obj.wpyLocX = obj.wpyLocY = 0 #BUG
      wpyphysTk.call("pack", menu, "-in", self.wpyphysTopName,
            "-side", "top", "-fill", "x")
      wpyphysTk.call("focus", menu)
    self.wpyphysHScrollName = None
    self.wpyphysVScrollName = None
    if self.wpyHasVScroll and self.wpyHasHScroll:
      name = self.wpyphysTopName
      t = ("HandleHScroll", name)
      if name == '.':
        frame = ".scrframe"
      else:
        frame = name + ".scrframe"
      name = frame + ".hscroll"
      box =  frame + ".scrbox"
      self.wpyphysHScrollName = name
      wpyphysTk.call("frame", frame, "-bd", "0")
      wpyphysTk.call("scrollbar", name, "-command", t, "-orient", "horizontal")
      h = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
      wpyphysTk.call("frame", box, "-width", h, "-height", h)
      wpyphysTk.call("pack", box, "-in", frame, "-side", "right")
      wpyphysTk.call("pack", name, "-in", frame,
             "-side", "left", "-expand", "1", "-fill", "x")
      wpyphysTk.call("pack", frame,
             "-in", self.wpyphysTopName,
             "-side", "bottom", "-fill", "x")
      self.WpyPhysChangeHScroll(self.wpyHScrollPos)
    elif self.wpyHasHScroll:
      name = self.wpyphysTopName
      t = ("HandleHScroll", name)
      if name == '.':
        name = ".hscroll"
      else:
        name = name + ".hscroll"
      self.wpyphysHScrollName = name
      wpyphysTk.call("scrollbar", name, "-command", t, "-orient", "horizontal")
      wpyphysTk.call("pack", name,
         "-in", self.wpyphysTopName,
         "-side", "bottom", "-fill", "x")
      self.WpyPhysChangeHScroll(self.wpyHScrollPos)
    if self.wpyHasVScroll:
      name = self.wpyphysTopName
      t = ("HandleVScroll", name)
      if name == '.':
        name = ".vscroll"
      else:
        name = name + ".vscroll"
      self.wpyphysVScrollName = name
      wpyphysTk.call("scrollbar", name, "-command", t)
      wpyphysTk.call("pack", name,
           "-in", self.wpyphysTopName,
           "-side", "right", "-fill", "y")
      self.WpyPhysChangeVScroll(self.wpyVScrollPos)
  def WpyPhysCreatePass2(self):
    wpyphysTk.call("pack", self.wpyphysFrameName, "-in", self.wpyphysTopName,
        "-expand", "1", "-fill", "both")
    wpyphysTk.call("pack", self.wpyphysTkName, "-in", self.wpyphysFrameName,
        "-expand", "1", "-fill", "both")
    wpyphysTk.call(self.wpyphysTkName, "configure",
         "-width", self.wpySizeX, "-height", self.wpySizeY)
    self.WpyPhysChangeVisible(self.wpyVisible)
  def WpyPhysDestroyWindow(self):
    wpyphysTk.call("destroy", self.wpyphysTopName)
  def WpyPhysChangeSize(self):
    self.wpyphysTopSizeX = -1
    wpyphysTk.call(self.wpyphysTkName, "configure",
         "-width", self.wpySizeX, "-height", self.wpySizeY)
    wpyphysTk.call("wm", "geometry", self.wpyphysTopName, "")
    wpyphysTk.call("update")
    self.wpyphysTopSizeX = string.atoi(
          wpyphysTk.call("winfo", "width",  self.wpyphysTopName))
    self.wpyphysTopSizeY = string.atoi(
          wpyphysTk.call("winfo", "height", self.wpyphysTopName))
  def WpyPhysChangeTitle(self, title):
    wpyphysTk.call("wm", "title", self.wpyphysTopName, title)
  def WpyPhysChangeVisible(self, visible):
    if visible:
      wpyphysTk.call("wm", "deiconify", self.wpyphysTopName)
    else:
      wpyphysTk.call("wm", "withdraw", self.wpyphysTopName)
  def WpyPhysChangeMouseMove(self, move):
    if move:
      t = ("HandleMouse", "%W", "m", "%b", "%x", "%y", "%s")
      wpyphysTk.call("bind", self.wpyphysTkName, "<Any-Motion>", t)
    else:
      wpyphysTk.call("bind", self.wpyphysTkName, "<Any-Motion>", "")
  def WpyPhysChangeHScroll(self, pos):
    if self.wpyHScrollSize <= self.wpyHScrollWinSize:
      wpyphysTk.call(self.wpyphysHScrollName, "set", "1", "1", "0", "0")
    else:
      wpyphysTk.call(self.wpyphysHScrollName, "set",
        self.wpyHScrollSize, self.wpyHScrollWinSize, pos,
        pos + self.wpyHScrollWinSize - 1)
  def WpyPhysChangeVScroll(self, pos):
    if self.wpyVScrollSize <= self.wpyVScrollWinSize:
      wpyphysTk.call(self.wpyphysVScrollName, "set", "1", "1", "0", "0")
    else:
      wpyphysTk.call(self.wpyphysVScrollName, "set",
        self.wpyVScrollSize, self.wpyVScrollWinSize, pos,
        pos + self.wpyVScrollWinSize - 1)

class WpyPhysChildWindow(WpyPhysWindow):
# Note: wpyphysTkName refers to the canvas, while wpyphysTopName
# is the container window.
  def WpyPhysCreateWindow(self):
    self.WpyPhysPrivatePass1()
    self.WpyPhysPrivatePass2()
  def WpyPhysCreatePass1(self):
    global wpyphysSequence
    global wpyphysNamesToPhys
    self.wpyphysTopName = topname = self.WpyPhysNewName()
    wpyphysNamesToPhys[topname] = self
    wpyphysTk.call("frame", topname)
    self.wpyphysFrameName = frame = topname + ".cframe"
    self.wpyphysTkName = canvas = frame + ".canvas"
    wpyphysNamesToPhys[canvas] = self
    wpyphysTk.call("frame", frame, "-bd", wpyphysCanvasBd,
           "-relief", wpyphysCanvasRelief)
    wpyphysTk.call("canvas", canvas, "-bd", "0")
    self.wpyFrameSizeX = self.wpyFrameSizeY = wpyphysCanvasBd + wpyphysCanvasBd
    self.wpyphysWrItems = []
    self.wpyphysHScrollName = None
    self.wpyphysVScrollName = None
    if self.wpyHasVScroll and self.wpyHasHScroll:
      name = self.wpyphysTopName
      t = ("HandleHScroll", name)
      if name == '.':
        frame = ".scrframe"
      else:
        frame = name + ".scrframe"
      name = frame + ".hscroll"
      box =  frame + ".scrbox"
      self.wpyphysHScrollName = name
      wpyphysTk.call("frame", frame, "-bd", "0")
      wpyphysTk.call("scrollbar", name, "-command", t, "-orient", "horizontal")
      h = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
      wpyphysTk.call(frame, "configure", "-height", h)
      wpyphysTk.call("frame", box, "-width", h, "-height", h, "-bd", "0")
      wpyphysTk.call("pack", box, "-in", frame, "-side", "right")
      wpyphysTk.call("pack", name, "-in", frame,
             "-side", "left", "-expand", "1", "-fill", "x")
      wpyphysTk.call("pack", frame,
             "-in", self.wpyphysTopName,
             "-side", "bottom", "-fill", "x")
      self.wpyFrameSizeY = self.wpyFrameSizeY + h
      self.WpyPhysChangeHScroll(self.wpyHScrollPos)
    elif self.wpyHasHScroll:
      name = self.wpyphysTopName
      t = ("HandleHScroll", name)
      if name == '.':
        name = ".hscroll"
      else:
        name = name + ".hscroll"
      self.wpyphysHScrollName = name
      wpyphysTk.call("scrollbar", name, "-command", t, "-orient", "horizontal")
      h = string.atoi(wpyphysTk.call("winfo", "reqheight", name))
      wpyphysTk.call("pack", name,
         "-in", self.wpyphysTopName,
         "-side", "bottom", "-fill", "x")
      self.wpyFrameSizeY = self.wpyFrameSizeY + h
      self.WpyPhysChangeHScroll(self.wpyHScrollPos)
    if self.wpyHasVScroll:
      name = self.wpyphysTopName
      t = ("HandleVScroll", name)
      if name == '.':
        name = ".vscroll"
      else:
        name = name + ".vscroll"
      self.wpyphysVScrollName = name
      wpyphysTk.call("scrollbar", name, "-command", t)
      w = string.atoi(wpyphysTk.call("winfo", "reqwidth", name))
      wpyphysTk.call("pack", name,
           "-in", self.wpyphysTopName,
           "-side", "right", "-fill", "y")
      self.wpyFrameSizeX = self.wpyFrameSizeX + w
      self.WpyPhysChangeVScroll(self.wpyVScrollPos)
    wpyphysTk.call("pack", self.wpyphysFrameName, "-in", self.wpyphysTopName,
        "-expand", "1", "-fill", "both")
    wpyphysTk.call("pack", self.wpyphysTkName, "-in", self.wpyphysFrameName,
        "-expand", "1", "-fill", "both")
  def WpyPhysCreatePass2(self):
    self.WpyPhysChangeSize()
  def WpyPhysDestroyWindow(self):
    wpyphysTk.call("destroy", self.wpyphysTopName)
  def WpyPhysChangeSize(self):
    if self.wpyVisible:
      wpyphysTk.call("place", self.wpyphysTopName,
           "-x", int(self.wpyLocX), "-y", int(self.wpyLocY),
           "-width", int(self.wpySizeX + self.wpyFrameSizeX),
           "-height", int(self.wpySizeY + self.wpyFrameSizeY))
  def WpyPhysChangeTitle(self, title):
    pass
  def WpyPhysChangeMouseMove(self, move):
    if move:
      t = ("HandleMouse", "%W", "m", "%b", "%x", "%y", "%s")
      wpyphysTk.call("bind", self.wpyphysTkName, "<Any-Motion>", t)
    else:
      wpyphysTk.call("bind", self.wpyphysTkName, "<Any-Motion>", "")
  def WpyPhysChangeVisible(self, visible):
    if visible:
      wpyphysTk.call("place", self.wpyphysTopName,
           "-x", int(self.wpyLocX), "-y", int(self.wpyLocY),
           "-width", int(self.wpySizeX + self.wpyFrameSizeX),
           "-height", int(self.wpySizeY + self.wpyFrameSizeY))
    else:
      wpyphysTk.call("place", "forget", self.wpyphysTopName)
  def WpyPhysChangeHScroll(self, pos):
    if self.wpyHScrollSize <= self.wpyHScrollWinSize:
      wpyphysTk.call(self.wpyphysHScrollName, "set", "1", "1", "0", "0")
    else:
      wpyphysTk.call(self.wpyphysHScrollName, "set",
        self.wpyHScrollSize, self.wpyHScrollWinSize, pos,
        pos + self.wpyHScrollWinSize - 1)
  def WpyPhysChangeVScroll(self, pos):
    if self.wpyVScrollSize <= self.wpyVScrollWinSize:
      wpyphysTk.call(self.wpyphysVScrollName, "set", "1", "1", "0", "0")
    else:
      wpyphysTk.call(self.wpyphysVScrollName, "set",
        self.wpyVScrollSize, self.wpyVScrollWinSize, pos,
        pos + self.wpyVScrollWinSize - 1)
