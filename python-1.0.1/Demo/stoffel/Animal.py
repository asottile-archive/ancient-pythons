# Animal.Py: translated from Logo (92/9)

import string

def Explain():
  Clr_scr()
  print 'In this game, the computer accumulates'
  print 'knowledge about animals by trying to'
  print 'guess what animal you are thinking of.'
  print 'If it doesn\'t know, it will ask you to'
  print 'teach it something and incorporate'
  print 'this knowledge in the next stage of'
  print 'the game.'
  print
  print 'When you start the game, the computer'
  print 'already knows about a few animals.'
  print


def Initialize_knowledge():
  if 'yes' == Ask_yes_or_no('Do you want to start from scratch?'):
    Knowledge = 'hippo'
  else:
    file = open('Animal.Lst', 'r')
    Knowledge = eval(file.read())
    file.close()
    #--print 'Read in from disk:\n', Knowledge #Temp
  return Knowledge


def Save_the_data():
  global Knowledge
  print '\nInfo:\n', Knowledge  # debug
  if 'yes' == Ask_yes_or_no('Do you want to save the info to disk?'):
    file = open('Animal.Lst', 'w')
    file.write(`Knowledge`)
    file.close()
    print 3*'\t', '>>> 1 list/string written to disk <<<'


def Play_animal():
  global Knowledge
  Clr_scr()
  print
  print 'Think of an animal...\n'
  print 'I will try to guess it by asking questions.'
  print
  Guess(Knowledge)
  if 'yes' == Ask_yes_or_no('Do you want to try again?'):
    Play_animal()
  else:
    print '\256\256\256 Ok, till some other time then. \257\257\257'


def Guess(choices):
  if type(choices) == type(''):
     Final_guess(choices)
     return 
  response =  Ask_yes_or_no(Next_question(choices))
  if response == 'yes':
    Guess(Yes_branch(choices))
    return
  Guess(No_branch(choices))


def Next_question(tree):  return first(tree)
def No_branch(tree):      return last(tree)
def Yes_branch(tree):     return tree[1]  # 2nd elt


def Ask_yes_or_no(question):
  resp  =  raw_input('\n'+question+' ')
  if first(resp) in 'yY': return 'yes'
  if first(resp)  in 'nN': return 'no'
  print 'Please type yes or no: ',  # (in lowercase)?
  return Ask_yes_or_no(question)


def Final_guess(choice):
  final_question =  'Is it '+ Add_a_or_an(choice)+'?'
  response =  Ask_yes_or_no(final_question)
  if response == 'yes':
    print 3*'\t', '\257\257\257\257\257\257\257  Look how smart I am! \n'
    return
  Get_smarter(choice)


def Add_a_or_an(word):
  if first(word) in 'aeiou':
    return ('an '+word)
  else:
    return ('a '+word)


def Get_smarter(Wrong_answer):
  Right_answer = raw_input('\nOh well, I was wrong. What was it? ')
  if Right_answer[:2] == 'a ': Right_answer = Right_answer[2:]
  elif Right_answer[:3] == 'an ': Right_answer = Right_answer[3:]
  print '\nPlease type in a question whose answer is'
  print 3*' ', vdu_bold('yes'), 'for', Add_a_or_an(Right_answer), 'and'
  print 3*' ', vdu_bold('no'), 'for', Add_a_or_an(Wrong_answer)+':'
  question = raw_input()
  question = string.upper(question[0]) + question[1:]
  if last(question) != '?': question = question + '?'
  Expand_knowledge(question, Right_answer, Wrong_answer)


def Expand_knowledge(New_question, Right_answer, Wrong_answer):
  global Knowledge
  Knowledge = Replace(Knowledge, Wrong_answer, \
                      [New_question,Right_answer,Wrong_answer])
  print '\n', Knowledge  # debug


def Replace(Data, word, New_branch):
  if Data == word: return New_branch
  if type(Data) == type(''): return Data
  return [Next_question(Data), Replace(Yes_branch(Data), word, New_branch), \
                               Replace( No_branch(Data), word, New_branch)]


def first(x):  return x[0]
def last(x):   return x[-1]
def Clr_scr():     print  '\033[2J',
def vdu_bold(s):   return '\033[1m'+s+'\033[0m'

Explain()
Knowledge = Initialize_knowledge()
Play_animal()
Save_the_data()

