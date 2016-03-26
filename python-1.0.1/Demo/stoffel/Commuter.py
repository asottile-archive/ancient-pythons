#module Commuter

from string import ljust, center

lj = ljust

MaxQ = 5  # const

class Person:
   def __init__(self):  # proc
      self.name = None
      self.surname = None
      self.job = None
      self.dest = None
      self.sport = None

   def show(self):  # proc
      if self.name: print lj(self.name, 12),
      else: print center('-', 12),
      if self.surname: print lj(self.surname, 12),
      else: print center('-', 12),
      if self.job: print lj(self.job, 12),
      else: print center('-', 12),
      if self.dest: print lj(self.dest, 12),
      else: print center('-', 12),
      if self.sport: print lj(self.sport, 12)
      else: print center('-', 12)



# Introduce symbols:
Bert = 'Bert'; Bill = 'Bill'; Fred = 'Fred'; John = 'John'; Sam = 'Sam'
Alberts = 'Alberts'; Fredericks = 'Fredericks'; Johnson = 'Johnson'; Samson = 'Samson'; Williams = 'Williams'
bricklayer = 'bricklayer'; carpenter = 'carpenter'; plumber = 'plumber'; printer = 'printer'; welder = 'welder'
Heathfield = 'Heathfield'; Kalk_Bay = 'Kalk_Bay'; Lakeside = 'Lakeside'; Retreat = 'Retreat'; Wynberg = 'Wynberg'
cycling = 'cycling'; darts = 'darts'; snooker = 'snooker'; soccer = 'soccer'; tennis = 'tennis'

Sym_dict = { \
   'name':    ['Bert', 'Bill', 'Fred', 'John', 'Sam'], \
   'surname': ['Alberts', 'Fredericks', 'Johnson', 'Samson', 'Williams'], \
   'job':     ['bricklayer', 'carpenter', 'plumber', 'printer', 'welder'], \
   'dest':    ['Heathfield', 'Kalk_Bay', 'Lakeside', 'Retreat', 'Wynberg'], \
   'sport':   ['cycling', 'darts', 'snooker', 'soccer', 'tennis'] }

All_symbols = []
for prop in Sym_dict.keys():
   All_symbols = All_symbols + Sym_dict[prop]


def NotePosition(symbol, p):  # proc
  global Q, StillToBePlaced
  if symbol in StillToBePlaced:
     StillToBePlaced.remove(symbol)
     setattr(Q[p], attrib(symbol), symbol)
     print symbol,  # debug
  #else:
  #   print symbol, p, 'already removed'  # debug


def attrib(v):  # func -> Sym_dict.keys()
  global Sym_dict
  for prop in Sym_dict.keys():
     if v in Sym_dict[prop]:
          return prop
  return None

def Has(prop, p):  # func boolean
  global Q
  return getattr(Q[p], prop)


def FindVacancies(Ty1, Ty2, r):  # proc
  PositionSet = []
  for p in range(1, 1+MaxQ - r):
     if not Has(Ty1,p):
        if not Has(Ty2,p+r):
           PositionSet.append(p)  #(p,p+r) ?
           if r > 0 : PositionSet.append(p+r)
  #loop
  return PositionSet


def TryElimination(v1, v2, r):  # proc
  global PossiblePositions, attrib
  PossiblePositions = FindVacancies(attrib(v1), attrib(v2), r)
  card = len(PossiblePositions)
  if (r == 0) and (card == 1) or (r > 0) and (card == 2):
     for p in range(1, 1+MaxQ-r):
        if p in PossiblePositions:
           NotePosition(v1, p)
           NotePosition(v2, p+r)
           return


def NoteBehind(v1, v2, r):  # proc
  global Q, StillToBePlaced
  if (v1 in StillToBePlaced) and (v2 in StillToBePlaced):
     TryElimination(v1, v2, r)
  else:
     for p in range(1, 1+MaxQ - r):
        if v1 == getattr(Q[p], attrib(v1)):
             NotePosition(v2, p+r)
             return
        if v2 == getattr(Q[p+r], attrib(v2)):
             NotePosition(v1, p)
             return
     #loop


def NoteThat(v1, v2):  # proc
  NoteBehind(v1, v2, 0)


Q = [None]  # Dummy person in position 0
for p in range(1, MaxQ+1):
   Q.append(Person())

StillToBePlaced = All_symbols
count = len(StillToBePlaced)

while 1:
   NoteThat(Fred, welder)
   NotePosition(printer, 2)
   NoteThat(Fredericks, Retreat)
   NoteThat(Samson, Kalk_Bay)
   NoteBehind(Bert, plumber, 3)
   NoteThat(John, soccer)
   NotePosition(snooker, 3)
   NotePosition(Lakeside, 1)
   NoteThat(Retreat, tennis)
   NotePosition(Bill, 4)
   NoteThat(carpenter, cycling)
   NoteBehind(darts, Johnson, 1)
   NotePosition(Williams, 5)
   NoteThat(plumber, Wynberg)
   NoteBehind(Alberts, Samson, 1)
   NoteBehind(printer, Johnson, 1)
   NoteBehind(Sam, Kalk_Bay, 1)
   NoteBehind(Heathfield, bricklayer, 1)

   if len(StillToBePlaced) == count: break  # No further progress!
   count = len(StillToBePlaced)

   print '\n', len(StillToBePlaced), 'symbols left\n'  # debug
   #for p in range(1, MaxQ+1): Q[p].show()

   if StillToBePlaced == []: break
#loop

print
for p in range(1, MaxQ+1):
   print `p`, ':',
   Q[p].show()
#loop


