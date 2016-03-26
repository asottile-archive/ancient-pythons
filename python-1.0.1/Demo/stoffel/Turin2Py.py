# -- Turin2Py.py, 92-9-8

import string
from regex import match, search

def Translate_file(inf, outf):
   while 1:
      line = inf.readline()
      print len(line), 'char(s):', line,
      if line == '': return

      #string.expandtabs(line,4):
      while '\t' in line:
         i = search('\t', line)
         line = line[:i] + 4*' ' + line[i+1:]

      while '"' in line:
         i = search('"', line)
         line = line[:i] + '\'' + line[i+1:]

      if line == chr(10):  outf.write(line);  continue

      ls = match(' *', line)  # Leading spaces
      i = search('%',    line)
      if i >= 0: line = line[:i] + '#' + line[i+1:]

      i = match(' *var ', line)
      if i >= 0: line = '#'+line

      i = match(' *type ', line)
      if i >= 0: line = '#'+line

      i = match('const ', line)
      if i >= 0: line = line[i+6:-1] + '# const\n'

      if match(' *end ', line) >= 0:
         i = search('end', line)
         line = line[:i] + '#' + line[i:]  #continue?

      i = search(' = ', line)   # Comparison
      if i >= 0:
         line = line[:i] + ' == ' + line[i+3:]
      else:
         i = search(':=',   line)
         if i >= 0: line = line[:i] + line[i+1:]

      if match(' *put ', line) >= 0:
         i = search('put ', line)
         line = line[:i] + 'print ' + line[i+4:]
         i = search(' skip', line)
         if i >= 0: line = line[:i] + ' \'\\n\'' + line[i+5:]
         i = search(' \.\.\n', line)
         if i >= 0: line = line[:i] + ',\n'

      if match(' *get ', line) >= 0:
         i = search('get ', line)
         line = line[:i] + line[i+4:-1] + ' = input()\n'

      if match(' *loop', line) >= 0:
         i = search('loop', line)
         line = line[:i] + 'while 1:' + line[i+4:]

      if match(' *exit when', line) >= 0:
         i = search('exit', line)
         line = line[:i] + 'if'+ line[i+9:-1] + ': break\n'

      if match(' *for .*:', line) >= 0:
         i = search(':', line)
         j = search('\.\.', line)
         line = line[:i] + 'in range(' + line[i+2:j-1] + ',' + line[j+2:-1] +'):\n'

      if match('fcn', line) >= 0 or match('func', line) >= 0 or match('proc', line) >= 0:
         i = search(' ', line)
         line = 'def' + line[i:-1] + ':  #' + line[:i] + '\n'

      i = search('result ', line)
      if i >= 0: line = line[:i] + 'return' + line[i+6:]

      i = search(' then', line)
      if i >= 0: line = line[:i] + ':\n'

      i = search('elsif', line)
      if i >= 0: line = line[:i] + 'elif' + line[i+5:]

      i = search('else[ \n]', line)
      if i >= 0: line = line[:i] + 'else:' + line[i+4:]

      i = search(' mod ', line)
      if i >= 0: line = line[:i] + ' % ' + line[i+5:]

      i = search(' div ', line)
      if i >= 0: line = line[:i] + ' / ' + line[i+5:]

      i = search('\+\=', line)   # Augmented assignment
      if i >= 0: line = line[:i] + '= ' + line[ls:i] + '+' + line[i+2:]

      print len(line), 'char(s):', line
      outf.write(line)

print
#filename = 'Kahrs'
filename = raw_input('Enter DOS filename: ')
inf  = open(filename+'.T', 'r'); inf
outf = open(filename+'.py', 'w'); outf
Translate_file(inf, outf)
inf.close()
outf.close()
print '. End Turin2Py /'
