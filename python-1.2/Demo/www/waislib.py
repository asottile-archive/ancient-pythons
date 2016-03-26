# WAIS client interface, based on the waisq model.
# This accurately parses the waisq question file, so no surprises!
# (XXX But the parser is too slow...)


import waisqp
import tempfile
import os


# The waisq program.  XXX Rely on user's $PATH
WAISQ = 'waisq -c /ufs/guido/src/wais/wais-sources/'


# Question class.  Normal usage:
# >>> q = Question()
# >>> q.set_seed_words('some interesting phrase')
# >>> q.add_source('foobar.src')
# >>> ...
# >>> q.do_query()
# >>> for x in q.get_result_summary(): print x
# To print document number i (0 <= i < number-of-documents):
# >>> q.write_document(i, sys.stdout)
# or, e.g.:
# >>> q.pipe_document(i, '/usr/ucb/more')
# or:
# >>> print q.get_document(i)
#
class Question:
	#
	def __init__(self):
		self.seed_words = ''
		self.sources = []
		self.relevant_documents = waisqp.List()
		self.result_documents = waisqp.List()
		self.scratch = tempfile.mktemp()
	#
	def close(self):
		try:
			os.unlink(self.scratch)
		except os.error:
			pass
	#
	def set_seed_words(self, seed_words):
		self.seed_words = seed_words
	#
	def get_seed_words(self):
		return self.seed_words
	#
	def add_source(self, source):
		self.sources.append(source)
	#
	def reset_sources(self):
		self.sources = []
	#
	def get_sources(self):
		return self.sources
	#
	def get_result_documents(self):
		return self.result_documents
	#
	def do_query(self):
		qrec = waisqp.Record('question')
		qrec['version'] = '2'
		qrec['seed-words'] = '"' + self.seed_words + '"'
		qrec['relevant-documents'] = self.relevant_documents
		slist = waisqp.List()
		for source in self.sources:
			s = waisqp.Record('source-id')
			s['filename'] = '"' + source + '"'
			slist.append(s)
		qrec['sources'] = slist
		file = self.scratch
		f = open(file, 'w')
		f.write(`qrec`)
		f.close()
		sts = os.system(WAISQ + ' -f ' + file + ' -g; echo 1>&2\n')
		if sts != 0:
			raise RuntimeError, 'waisq exit status ' + `sts`
		record = waisqp.parsefile(file)
		if record.gettype() <> 'question':
			raise RuntimeError, 'waisq did not write a question'
		self.result_documents = record['result-documents']
	#
	def get_result_summary(self):
		summary = []
		for doc in self.result_documents:
			score = doc['score']
			doc = doc['document']
			headline = doc['headline']
			lines = doc['number-of-lines']
			bytes = doc['number-of-bytes']
			type = doc['type']
			date = doc['date']
			rec = score, headline, lines, bytes, type, date
			summary.append(rec)
		return summary
	#
	def get_document(self, i):
		if not 0 <= i < len(self.result_documents):
			raise IndexError, 'document number out of range'
		cmd = WAISQ + ' -f ' + self.scratch + ' -v ' + `i+1` + '\n'
		p = os.popen(cmd, 'r')
		data = p.read()
		sts = p.close()
		if sts:
			sys.stderr.write('waisq exit status ' + `sts` + '\n')
		return data
	#
	def pipe_document(self, i, backend):
		if not 0 <= i < len(self.result_documents):
			raise IndexError, 'document number out of range'
		cmd = WAISQ + ' -f ' + self.scratch + ' -v ' + `i+1`
		cmd = cmd + ' | ' + backend + '\n'
		sts = os.system(cmd)
		if sts:
			sys.stderr.write('pipe_document exit status ' + \
				`sts` + '\n')
	#
	def write_document(self, i, f, *rest):
		if rest:
			if len(rest) > 1: raise TypeError, 'too many arguments'
			bufsize = rest[0]
		else:
			bufsize = 8192
		if not 0 <= i < len(self.result_documents):
			raise IndexError, 'document number out of range'
		cmd = WAISQ + ' -f ' + self.scratch + ' -v ' + `i+1` + '\n'
		p = os.popen(cmd, 'r')
		while 1:
			buf = p.read(bufsize)
			if not buf: break
			f.write(buf)
		sts = p.close()
		if sts:
			sys.stderr.write('waisq exit status ' + `sts` + '\n')


# Test program.
# usage: python -c 'import waislib;waislib.test()' database word ...
#
def test():
	import sys, string
	if len(sys.argv) < 3:
		sys.stderr.write('usage: test database word ...\n')
		sys.exit(2)
	db = sys.argv[1]
	if db[-4:] <> '.src': db = db + '.src'
	q = Question()
	try:
		q.add_source(db)
		q.set_seed_words(string.join(sys.argv[2:]))
		q.do_query()
		K = 1024
		i = 0
		summary = q.get_result_summary()
		for rec in summary:
			score, headline, lines, bytes, type, date = rec
			bytes = eval(bytes)
			print i+1, score, `(bytes+K-1)/K` + 'K', type, date, \
				headline
			reply = raw_input('retrieve this document? [yn](n) ')
			if string.lower(string.strip(reply)[:1]) == 'y':
				if summary[i][4] == '"MIME"':
					q.pipe_document(i, 'metamail')
				else:
					q.pipe_document(i, '${PAGER-more}')
			i = i+1
	finally:
		q.close()
