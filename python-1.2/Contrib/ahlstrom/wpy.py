# This is the file "wpy.py".  It contains all the class definitions,
# globals, etc. for Windowing Python.  Your app should import it.
# It is Copyright (C) 1994, but is freely distributable.  THERE ARE
# NO WARRANTIES AT ALL, USE AT YOUR OWN RISK.
# Comments to:  Jim Ahlstrom        jim@interet.com.
#
# The code in this file is intended to be mostly independent of
# the operating system GUI.  The module "wpy_phys.py" contains those
# dependencies, and this module inherits them.  Please do not import
# "wpy_phys.py" into your app.

# All widgets have a "title".  Even if this is not needed, it can be
# used for debugging.  All instance variables start with "wpy" and
# all methods (functions) and class names start with "Wpy" to avoid
# name conflicts with your app.  The names "wpyphys" in upper/lower case
# are used by wpy_phys.py and are considered private.

# Class hierarchy:
#
# WpyEvent,  a generic event class.
# WpyApp, the application, size is screen size, only one instance allowed.
#   WpyWidget, an abstract class, the parent of all widgets.
#
#     WpyMenuBar, the menu bar at the top of a top-level window.
#     WpyBarPopup, a pop-up menu used on a menu bar.
#     WpyTopPopup, a pop-up menu which can be posted to a window.
#     WpyMenuButton, pop-up item, press to execute a command.
#     WpyMenuCheck, pop-up item, press to select an item.
#     WpyMenuLine, pop-up item, a separator, not interactive.
#     WpyMenuPopup, a pop-up menu used as an item in another menu.
#     WpyMenuRadio, pop-up item, press to select one of a group.
#
#     WpyButton, a control, can be pressed with the mouse button
#     WpyCheckButton, a control, any of N selection button.
#     WpyLabel, a control, contains a single line of static text.
#     WpyMessage, a control, contains multiple lines of static text.
#     WpyRadioButton, a control, one of N selection button.
#     WpyScroll, a control, a scroll bar placed inside a window.
#
#     WpyTopLevel, a top-level (document) window.  First is main window.
#     WpyDialog, a dialog box for user interaction, a top-level window
#     WpyModalDialog, a dialog box for user interaction, a top-level window.

from wpy_phys import *

wpyVersion = "0.1"

_wpyApp = None
wpyBadChildWindow = "Child window must have another window as parent"
wpyNoApp = "Must call WpyApp first.  TopLevel is child of app."

# Defined flag bits.
wpyFlagsWindow	= 1	# Instance is a toplevel, child or dialog window
wpyFlagsDialog	= 2	# Instance is a dialog window


class WpyEvent:
# This is a generic event.  Instances are sent to event handlers.
# The event handlers have the call "Handler(object, event)" where
# "object" is the window where the event occured. The "Handler" may
# be either a function or a class method, and the system will adjust the
# call when sending the event.  NOTE that some handlers are called with
# a "None" event.
  def __init__(self):
    self.wpyTitle = "event"

wpye = WpyEvent()
wpyTypeMeth = type(wpye.__init__)
del wpye

class WpyApp(WpyPhysApp):
# Represents the whole application, and is the ultimate parent of all
# visible objects (windows and widgets).  It has the size of the screen.
# It is not a visible object itself.
  def __init__(self):
    global _wpyApp
    _wpyApp = self
    self.wpyTitle  = "Main App"
    self.wpyParent = None
    self.wpyChildList = []
    self.wpyFlags = 0
    self.wpyVisible = 0
    self.WpyPhysAppInit()	# Set up system metrics.
    WpyWidget.wpyScreenSizeX = self.wpySizeX
    WpyWidget.wpyScreenSizeY = self.wpySizeY
    WpyWidget.wpyCharSizeX = self.wpyCharSizeX
    WpyWidget.wpyCharSizeY = self.wpyCharSizeY
    WpyWidget.wpyOneMeter = self.wpyOneMeter
  def WpyMainLoop(self):
  # Call this to create all windows and start processing events.
    self.wpyCreated = 1
    self.WpyPhysMainLoop()
  def WpyExit(self = None, event = None):
  # Just a handy exit function in event handler format.
    import sys
    sys.exit(0)

class WpyWidget(WpyApp):
# Not intended to be instantiated.  Just used as a parent for all
# widgets.  It provides for common methods which are different for WpyApp.
  wpyScreenSizeX = 0
  wpyScreenSizeY = 0
  wpyOneMeter = 0
  wpyCharSizeX = 0
  wpyCharSizeY = 0
  wpyAnchor = "nw"
  wpyCreated = 0
  wpyVisible = 1
  wpyEnabled = 1
  wpyTraps = {}

  def __init__(self):
    pass

# Start of geometry management functions.

  def WpyMakeEqualSize(self, *args):
  # Handy function to make all sizes equal to the largest.
  # Call with arguments and/or lists and/or tuples.
  # It only works one level of lists down (no list of lists).
  # The "self" is not used.
    x = y = 0
    for obj in args:
      if type(obj) == type([]) or type(obj) == type(()):
        for item in obj:
            if x < item.wpySizeX: x = item.wpySizeX
            if y < item.wpySizeY: y = item.wpySizeY
      else:
          if x < obj.wpySizeX: x = obj.wpySizeX
          if y < obj.wpySizeY: y = obj.wpySizeY
    for obj in args:
      if type(obj) == type([]) or type(obj) == type(()):
        for item in obj:
            item.wpySizeX = x
            item.wpySizeY = y
      else:
          obj.wpySizeX = x
          obj.wpySizeY = y

  def WpyMakeEqualSpaceX(self, loc1, loc2, pos, anchor, objs):
  # Call with a tuple or list of objects.  Space "objs" equally in
  # the X direction in "self" between relative positions loc1 and
  # loc2, and place the "anchor" y-position at "pos".  loc1 and loc2
  # and pos must be between 0 and 1.
    tot = 0
    for ob in objs:
      tot = tot + ob.wpySizeX + ob.wpyFrameSizeX
    refsize = (loc2 - loc1) * self.wpySizeX
    offset = max(0.0, (refsize - tot) / float(len(objs) + 1))
    x = loc1 * self.wpySizeX + offset
    pos = pos * self.wpySizeY
    for ob in objs:
      obsizey = ob.wpySizeY + ob.wpyFrameSizeY
      ch = anchor[0]
      if ch == "s":
        y = pos - obsizey
      elif ch != "n":
        y = pos - obsizey / 2
      else:
        y = pos
      ob.wpyLocX = int(x)
      ob.wpyLocY = int(y)
      x = x + ob.wpySizeX + offset

  def WpyPlace(self, ref, locx, locy, anchor = "nw"):
  # Place self at locx,locy relative to reference window ref.
  # If ref is None, then locx,locy is in pixels.  Otherwise, locx
  # equal to 0/1.000 means the left/right edge of ref.  The
  # "anchor" means the point of self to place at the indicated position.
  # All sizes and locations refer to the client area of the window.
    if ref == None:
      mylocx = locx
      mylocy = locy
    elif ref.wpyFlags & wpy.wpyFlagsWindow:	# Is this a window?
      mylocx  = ref.wpySizeX * locx
      mylocy  = ref.wpySizeY * locy
    else:			# Not a window; transform coords.
      mylocx  = ref.wpyLocX +\
                 ref.wpySizeX * locx
      mylocy  = ref.wpyLocY +\
                 ref.wpySizeY * locy
    selfsizex = self.wpySizeX + self.wpyFrameSizeX
    selfsizey = self.wpySizeY + self.wpyFrameSizeY
    ch = anchor[0]
    if ch == "s":
      mylocy = mylocy - selfsizey
    elif ch != "n":
      mylocy = mylocy - selfsizey / 2
    ch = anchor[-1]
    if ch == "e":
      mylocx = mylocx - selfsizex
    elif ch != "w":
      mylocx = mylocx - selfsizex / 2
    self.wpyLocX = int(mylocx)
    self.wpyLocY = int(mylocy)

  def WpyGlue(self, ref, locx, locy, anchor, szx, szy):
  # Set the size of window "self" to szx,szy if the sizes are not None.
  # Then glue the point "anchor" of window "self" to the window "ref"
  # at the location locx,locy in ref.
  # All sizes and locations refer to the OUTSIDE of the windows.
    refsizex = ref.wpySizeX + ref.wpyFrameSizeX
    refsizey = ref.wpySizeY + ref.wpyFrameSizeY
    if ref == None:
      mylocx = locx
      mylocy = locy
      if szx != None:
        self.wpySizeX = int(szx - self.wpyFrameSizeX)
      if szy != None:
        self.wpySizeY = int(szy - self.wpyFrameSizeY)
    elif ref.wpyFlags & wpy.wpyFlagsWindow:	# Is this a window?
      mylocx  = refsizex * locx
      mylocy  = refsizey * locy
      if szx != None:
        self.wpySizeX = int(refsizex * szx - self.wpyFrameSizeX)
      if szy != None:
        self.wpySizeY = int(refsizey * szy - self.wpyFrameSizeY)
    else:			# Not a window; transform coords.
      mylocx  = ref.wpyLocX + refsizex * locx
      mylocy  = ref.wpyLocY + refsizey * locy
      if szx != None:
        self.wpySizeX = int(refsizex * szx - self.wpyFrameSizeX)
      if szy != None:
        self.wpySizeY = int(refsizey * szy - self.wpyFrameSizeY)
    selfsizex = self.wpySizeX + self.wpyFrameSizeX
    selfsizey = self.wpySizeY + self.wpyFrameSizeY
    ch = anchor[0]
    if ch == "s":
      mylocy = mylocy - selfsizey
    elif ch != "n":
      mylocy = mylocy - selfsizey / 2
    ch = anchor[-1]
    if ch == "e":
      mylocx = mylocx - selfsizex
    elif ch != "w":
      mylocx = mylocx - selfsizex / 2
    self.wpyLocX = int(mylocx)
    self.wpyLocY = int(mylocy)

  def WpyShrinkWrap(self):
  # Size an object to just fit all its children, and the point (0,0).
  # Assumes that all children fit in their parents.
    x1 = y1 = x2 = y2 = 0
    for object in self.wpyChildList:
      x = object.wpyLocX
      y = object.wpyLocY
      if x1 > x: x1 = x
      if y1 > y: y1 = y
      x = x + object.wpySizeX + object.wpyFrameSizeX
      y = y + object.wpySizeY + object.wpyFrameSizeY
      if x2 < x: x2 = x
      if y2 < y: y2 = y
    self.wpySizeX = x2 - x1
    self.wpySizeY = y2 - y1

# End of geometry management functions.

# Default event handlers so all events get handled.

  def WpyOnButton(self, event):
    print "WpyOnButton: ", self

  def WpyOnChar(self, event):
    print "In ", self.wpyphysTopName, " got num ", event.wpyKeyNum

  def WpyOnClose(self, event):
    self.WpyDestroyWindow()
    self.wpyDestroyedByClose = 1
    if not len(_wpyApp.wpyChildList):
      self.WpyExit()

  def WpyOnCreate(self, event):
    pass

  def WpyOnFocus(self, event):
    pass
    #print "Focus", self.wpyphysTkName, event.wpyFocusIn

  def WpyOnMouse(self, event):
  # Mouse press and mouse motion events.  Event attributes are:
  # wpyType	"p", "r", "d", "m" for press, release, double click, motion.
  # wpyLocX	x and y position of mouse in window coordinates.
  # wpyLocY
  # wpyPressed	The sum of the buttons currently pressed, B1=1, B2=2, B3=4.
  # wpyButton	For "m", zero.  Else the number of the button, 1, 2 or 3.
  # wpyShift	True if the Shift key is down.
  # wpyControl	True if the Control key is down.
    print "Mouse ", self.wpyphysTkName, event.wpyType,\
        event.wpyButton, event.wpyPressed, event.wpyLocX, event.wpyLocY,
    if event.wpyShift:
      print "Shift",
    if event.wpyControl:
      print "Control",
    print
    if event.wpyType == 'p':
      self.wpyMouseMove = 1
    elif event.wpyType == 'r':
      self.wpyMouseMove = 0

  def WpyOnScroll(self, event):
    self.wpyScrollPos = event.wpyScrollPos
    self.WpyChangeScroll()

# End of event handlers.

  def WpySendSizeEvent(self, event):
  # Resize events are sent top down.  Only top-level windows
  # can receive user-resize events.
    if self.wpyFlags & wpyFlagsWindow:
      if type(self.WpyOnSize) == wpyTypeMeth:
        self.WpyOnSize(event)
      else:
        self.WpyOnSize(self, event)
    self.WpyPhysChangeSize()
    for obj in self.wpyChildList:
      obj.WpySendSizeEvent(None)

  def WpyPrivateCreate(self):
  # Windows must be created with "CreateWindow()" before they are real.
    self.WpyCreatePass1()
    for object in self.wpyChildList:
      object.WpyPrivateCreate()


# Start of menus.

class WpyMenuBar(WpyWidget, WpyPhysMenuBar):
# A menu bar which can appear as the menu of a top-level window only.
# Add items to the menu bar with WpyBarPopup.
  def __init__(self, parent):
    self.wpyTitle = "menubar"
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    parent.wpyMenuBar = self
    self.wpyFlags = 0
    self.wpyMenuItems = []
    self.wpyFrameSizeX  = self.wpyFrameSizeY  = 0
    self.wpySizeX  = self.wpySizeY  = 0
    self.wpyLocX  = self.wpyLocY  = 0
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyEnabled"] = self.WpyChangeEnabled
  def WpyChangeEnabled(self, enabled):
    for object in self.wpyMenuItems:
      object.wpyEnabled = enabled

class WpyBarPopup(WpyWidget, WpyPhysBarPopup):
# An item in the menu bar of a top-level window.
  def __init__(self, parent, title):
    self.wpyTraps = {}
    self.wpyTitle = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    parent.wpyMenuItems.append(self)
    self.wpyFlags = 0
    self.wpyMenuItems = []
    self.wpyLocX  = self.wpyLocY  = 0
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    if not len(self.wpyMenuItems):
      self.wpyEnabled = 0
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyEnabled"] = self.WpyPhysChangeEnabled

class WpyTopPopup(WpyWidget, WpyPhysTopPopup):
# A pop-up menu which can be posted to a window.
# It starts out unposted.  To post, change self.wpyVisible to 1.
  def __init__(self, parent):
    self.wpyTraps = {}
    self.wpyTitle = "toppopup"
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    self.wpyFlags = 0
    self.wpyMenuItems = []
    self.wpyVisible = 0
    self.wpySizeX = self.wpySizeY = 100
    self.wpyLocX  = self.wpyLocY  = 0
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    if not len(self.wpyMenuItems):
      self.wpyEnabled = 0
    self.wpyTraps["wpyVisible"] = self.WpyChangeVisible
  def WpyChangeVisible(self, visible):
    if visible and self.wpyEnabled:
      self.WpyPhysChangeVisible(visible)
    elif not visible:
      self.WpyPhysChangeVisible(visible)

# Start of items in popup menus.

class WpyMenuButton(WpyWidget, WpyPhysMenuButton):
# Can only be used in a pop-up menu.
# A normal menu item which executes a command when it is selected.
# There is no wpyButtonValue for this type of button.
  def __init__(self, parent, title):
    self.wpyTraps = {}
    self.wpyTitle = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    parent.wpyMenuItems.append(self)
    self.wpyFlags = 0
    self.wpyButtonValue = None
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyEnabled"] = self.WpyPhysChangeEnabled

class WpyMenuCheck(WpyWidget, WpyPhysMenuCheck):
# Can only be used in a pop-up menu.
# A menu item which selects/unselects an option.
# The wpyButtonValue is 1/0 for selected/unselected.
  def __init__(self, parent, title):
    self.wpyTraps = {}
    self.wpyTitle = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    parent.wpyMenuItems.append(self)
    self.wpyFlags = 0
    self.wpyButtonValue = 0
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyEnabled"] = self.WpyPhysChangeEnabled

class WpyMenuRadio(WpyWidget, WpyPhysMenuRadio):
# Can only be used in a pop-up menu.
# A menu item which selects/unselects one of a group of options.
# The first radio button has no "group" argument, and is default "ON".
# Subsequent radio buttons have a group argument of the first button.
# All such radio buttons are grouped together and have self.wpyGroup equal
# to the class instance of the first button.  The wpyButtonValue of the
# first button is set to the instance of the selected button.
# Other radio buttons have wpyButtonValue "None".
# Therefore, the class instance of the selected button is available
# from any button as self.wpyGroup.wpyButtonValue.
# Also, the group leader (first button) has self.wpyGroup == self.
  def __init__(self, parent, title, group = None):
    self.wpyTraps = {}
    self.wpyTitle = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    parent.wpyMenuItems.append(self)
    self.wpyFlags = 0
    if group == None:
      self.wpyGroup = self
      self.wpyButtonValue = self	# this button is ON, the rest are OFF
    else:
      self.wpyGroup = group
      self.wpyButtonValue = None
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyEnabled"] = self.WpyPhysChangeEnabled

class WpyMenuLine(WpyWidget, WpyPhysMenuLine):
# Can only be used in a pop-up menu.
# A menu item which just draws a line between other items.  Not interactive.
  def __init__(self, parent):
    self.wpyTraps = {}
    self.wpyTitle = "menuline"
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    parent.wpyMenuItems.append(self)
    self.wpyFlags = 0
  def WpyCreatePass1(self):
    pass

class WpyMenuPopup(WpyWidget, WpyPhysMenuPopup):
# Can only be used in a pop-up menu.
# A menu item which pops up a cascaded pop-up menu.
  def __init__(self, parent, title):
    self.wpyTraps = {}
    self.wpyTitle = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    parent.wpyMenuItems.append(self)
    self.wpyFlags = 0
    self.wpyMenuItems = []
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyEnabled"] = self.WpyPhysChangeEnabled

# End of pop-up menu items.

# Start of controls.

class WpyBox(WpyWidget, WpyPhysBox):
  def __init__(self, parent, title):
    self.wpyTitle  = title
    self.wpyChildList = []
    self.wpyFlags = 0
    self.wpyAnchor = "nw"
    if parent != None:
      self.wpyParent = parent
      parent.wpyChildList.append(self)
    self.wpySizeX = self.wpySizeY = 100
    self.wpyLocX  = self.wpyLocY  = 0
    self.wpyFrameSizeX  = self.wpyFrameSizeY  = 3	# sets the frame size
  def WpyCreatePass1(self):
    pass

class WpyButton(WpyWidget, WpyPhysButton):
# A button the user can press with the mouse.  You must specify
# wpyLocX and wpyLocY yourself, but a default size is made.
# Parent must be specified, and must not be WpyApp.
# There is no wpyButtonValue for this type of button.
  def __init__(self, parent, title):
    self.wpyTraps = {}
    self.wpyTitle  = title
    self.wpyParent = parent
    self.wpyChildList = []
    self.wpyFlags = 0
    self.wpyButtonValue = None
    self.wpyAnchor = "center"
    parent.wpyChildList.append(self)
    self.wpyLocX  = self.wpyLocY  = 0
    # Size and units are set up by wpy_phys.
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyVisible"] = self.WpyPhysChangeVisible
    self.wpyTraps["wpyEnabled"] = self.WpyPhysChangeEnabled

class WpyCheckButton(WpyWidget, WpyPhysCheckButton):
# A check button the user can press with the mouse.  You must specify
# wpyLocX and wpyLocY yourself, but a default size is made.
# Parent must be specified, and must not be WpyApp.
# The wpyButtonValue is 1/0 for selected/unselected.
  def __init__(self, parent, title):
    self.wpyTraps = {}
    self.wpyTitle  = title
    self.wpyParent = parent
    self.wpyChildList = []
    self.wpyFlags = 0
    self.wpyButtonValue = 0
    self.wpyAnchor = "center"
    parent.wpyChildList.append(self)
    self.wpyLocX  = self.wpyLocY  = 0
    # Size and units are set up by wpy_phys.
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyVisible"] = self.WpyPhysChangeVisible
    self.wpyTraps["wpyEnabled"] = self.WpyPhysChangeEnabled
    
class WpyLabel(WpyWidget, WpyPhysLabel):
# A single line of text, not interactive.
  def __init__(self, parent, title):
    self.wpyTraps = {}
    self.wpyTitle  = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    self.wpyFlags = 0
    self.wpyLocX  = self.wpyLocY  = 0
    # Size and units are set up by wpy_phys.
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyVisible"] = self.WpyPhysChangeVisible

class WpyMessage(WpyWidget, WpyPhysMessage):
# A multi-line text message with justification, not interactive.
  def __init__(self, parent, title, aspect = 2.7, justify = "left"):
    self.wpyTraps = {}
    self.wpyTitle  = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    self.wpyFlags = 0
    self.aspect = aspect	# Aspect ratio width/height as a decimal.
    self.justify = justify	# left, right or center
    self.wpyLocX  = self.wpyLocY  = 0
    # Size and units are set up by wpy_phys.
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyVisible"] = self.WpyPhysChangeVisible

class WpyRadioButton(WpyWidget, WpyPhysRadioButton):
# A radio button the user can press with the mouse.  You must specify
# wpyLocX and wpyLocY yourself, but a default size is made.
# Parent must be specified, and must not be WpyApp.
# The first radio button has no "group" argument, and is default "ON".
# Subsequent radio buttons have a group argument of the first button.
# All such radio buttons are grouped together and have self.wpyGroup equal
# to the class instance of the first button.  The wpyButtonValue of the
# first button is set to the instance of the selected button.
# Other radio buttons have wpyButtonValue "None".
# Therefore, the class instance of the selected button is available
# from any button as self.wpyGroup.wpyButtonValue.
# Also, the group leader (first button) has self.wpyGroup == self.
  def __init__(self, parent, title, group = None):
    self.wpyTraps = {}
    self.wpyTitle  = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    self.wpyFlags = 0
    if group == None:
      self.wpyGroup = self
      self.wpyButtonValue = self	# this button is ON, the rest are OFF
    else:
      self.wpyGroup = group
      self.wpyButtonValue = None
    self.wpyAnchor = "center"
    self.wpyLocX  = self.wpyLocY  = 0
    # Size and units are set up by wpy_phys.
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyVisible"] = self.WpyPhysChangeVisible
    self.wpyTraps["wpyEnabled"] = self.WpyPhysChangeEnabled
  def WpyRadioButton(self, title):
    return WpyRadioButton(title, self.wpyParent, self)

class WpyScroll(WpyWidget, WpyPhysScroll):
# A scroll bar control.  Not used for scroll bar on window.
  def __init__(self, parent, title):
    self.wpyTraps = {}
    self.wpyTitle  = title	# Must start with "v" or "h"
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    self.wpyFlags = 0
    if title[0] == "v":
      self.wpyAnchor = "n"
    else:
      self.wpyAnchor = "w"
    self.wpyScrollSize = 0	# Total size of scrolled object.
    self.wpyScrollWinSize = 0	# Size which fits in the window.
    self.wpyScrollPos = 0	# Index of first line in the window.
    self.wpyLocX  = self.wpyLocY  = 0
    # Size and units are set up by wpy_phys.
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    pass
    #self.wpyTraps["wpyScrollSize"]	= self.WpyChangeScroll
    #self.wpyTraps["wpyScrollWinSize"]	= self.WpyChangeScroll
    #self.wpyTraps["wpyScrollPos"]	= self.WpyChangeScroll
  def WpyChangeScroll(self, pos = None):
    if pos == None:
      self.WpyPhysChangeScroll(self.wpyScrollPos)
    else:
      self.WpyPhysChangeScroll(pos)

# End of controls.

# Start of windows.

class WpyDialog(WpyWidget, WpyPhysDialog):
# A modeless dialog box, the way you get input from the user.  Many GUIs treat
# dialogs differently from windows by offering accelerator keys for example.
# Dialogs are always top-level windows.  They do not have scroll bars or
# size changing decorations, but may have a title bar and a close box.
# You can not use drawing functions on a dialog.
# Dialogs are either modal (forces user to dismiss dialog by destroying it)
# or modeless.
  def __init__(self, parent, title):
    if _wpyApp == None:
      raise wpyNoApp
    # parent is ignored.
    self.wpyTraps = {}
    self.wpyTitle  = title
    self.wpyParent = _wpyApp
    self.wpyChildList = []
    _wpyApp.wpyChildList.append(self)
    self.wpyFlags = wpyFlagsWindow + wpyFlagsDialog
    self.wpyDefaultButton = None
    self.wpyDestroyedByClose = 0
    self.wpySizeX = 100
    self.wpySizeY = 100
    self.wpyLocX = self.wpyLocY = 0
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyVisible"] = self.WpyPhysChangeVisible
  def WpyDestroyWindow(self):
    self.WpyPhysDestroyWindow()
    self.wpyParent.wpyChildList.remove(self)
  def WpyCreateWindow(self):
    if not self.wpyCreated:
      self.WpyPrivateCreate()
      self.WpyPhysCreateWindow()
  def WpyOnSize(self, event):
    pass
    
class WpyModalDialog(WpyWidget, WpyPhysModalDialog):
# See WpyDialog.
  def __init__(self, parent, title):
    if _wpyApp == None:
      raise wpyNoApp
    # parent is ignored.
    self.wpyTraps = {}
    self.wpyTitle  = title
    self.wpyParent = _wpyApp
    self.wpyChildList = []
    _wpyApp.wpyChildList.append(self)
    self.wpyFlags = wpyFlagsWindow + wpyFlagsDialog
    self.wpyDefaultButton = None
    self.wpyDestroyedByClose = 0
    self.wpySizeX = 100
    self.wpySizeY = 100
    self.wpyLocX = self.wpyLocY = 0
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyVisible = 1
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
  def WpyDestroyWindow(self):
    self.WpyPhysDestroyWindow()
    self.wpyParent.wpyChildList.remove(self)
  def WpyCreateWindow(self):
    if not self.wpyCreated:
      self.WpyPrivateCreate()
      self.WpyPhysCreateWindow()
  def WpyOnSize(self, event):
    pass

class WpyTopLevel(WpyWidget, WpyPhysTopLevel):
# All top-level windows move independently and have a title bar and
# a close box.  They can have a menu bar, size changing decorations, 
# scroll bars.  There may be other decorations such as iconify and zoom boxes.
# The first WpyTopLevel window is the "Main Window" (main widget in X).
# The client area of any window may contain controls, and is drawable.
  def __init__(self, parent, title):
    if _wpyApp == None:
      raise wpyNoApp
    if parent == None:
      parent = _wpyApp
    self.wpyTraps = {}
    self.wpyTitle  = title
    self.wpyParent = parent
    self.wpyChildList = []
    parent.wpyChildList.append(self)
    self.wpyFlags = wpyFlagsWindow
    self.wpyDefaultButton = None
    self.wpyDestroyedByClose = 0
    self.wpyMenuBar = None
    self.wpyHasResize = 0
    self.wpyHasVScroll = 0
    self.wpyHasHScroll = 0
    self.wpyHScrollSize = self.wpyVScrollSize = 0
    self.wpyHScrollWinSize = self.wpyVScrollWinSize = 0
    self.wpyHScrollPos = self.wpyVScrollPos = 0
    self.wpyMouseMove = 0
    self.wpySizeX = 100
    self.wpySizeY = 100
    self.wpyLocX = self.wpyLocY = 0
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreatePass1(self):
    self.wpyTraps["wpyTitle"] = self.WpyPhysChangeTitle
    self.wpyTraps["wpyVisible"] = self.WpyPhysChangeVisible
    self.wpyTraps["wpyMouseMove"] = self.WpyPhysChangeMouseMove
  def WpyDestroyWindow(self):
    self.WpyPhysDestroyWindow()
    self.wpyParent.wpyChildList.remove(self)
  def WpyCreateWindow(self):
    if not self.wpyCreated:
      self.WpyPrivateCreate()
      self.WpyPhysCreateWindow()
  def WpyOnHScroll(self, event):
    self.wpyHScrollPos = event.wpyScrollPos
    self.WpyChangeHScroll()
  def WpyOnVScroll(self, event):
    self.wpyVScrollPos = event.wpyScrollPos
    self.WpyChangeVScroll()
  def WpyChangeVScroll(self, pos = None):
    if pos == None:
      self.WpyPhysChangeVScroll(self.wpyVScrollPos)
    else:
      self.WpyPhysChangeVScroll(pos)
  def WpyChangeHScroll(self, pos = None):
    if pos == None:
      self.WpyPhysChangeHScroll(self.wpyHScrollPos)
    else:
      self.WpyPhysChangeHScroll(pos)
  def WpyOnSize(self, event):
    pass
    
class WpyChildWindow(WpyPhysChildWindow, WpyTopLevel):
# Child windows can have a scroll bars as their only decorations.
  def __init__(self, parent, title):
    if _wpyApp == None or parent == _wpyApp:
      raise wpyBadChildWindow
    WpyTopLevel.__init__(self, parent, title)
  def __setattr__(self, name, value):
    try:
      self.wpyTraps[name](value)
    except KeyError:
      pass
    self.__dict__[name] = value
  def WpyCreateWindow(self):
    if not self.wpyCreated:
      self.WpyPrivateCreate()
      self.WpyPhysCreateWindow()
