DESTDIR=/usr/local
LIBDESTDIR=$DESTDIR/lib
LIBDEST=$LIBDESTDIR/python
DOCDESTDIR=$LIBDEST/doc

all:	tut lib ref ext

tut:
	latex tut
	latex tut
	dvips tut >tut.ps

ref:
	touch ref.ind
	latex ref
	./fix_hack ref.idx
	makeindex ref
	latex ref
	dvips ref >ref.ps

lib:
	touch lib.ind
	latex lib
	./fix_hack lib.idx
	makeindex lib
	latex lib
	dvips lib >lib.ps

ext:
	touch ext.ind
	latex ext
	./fix_hack ext.idx
	makeindex ext
	latex ext
	dvips ext >ext.ps

qua:
	latex qua
	bibtex qua
	latex qua
	latex qua
	dvips qua >qua.ps

lib.texi: lib*.tex texipre.dat texipost.dat partparse.py
	python partparse.py -o @lib.texi `whichlibs`
	mv @lib.texi lib.texi

.PRECIOUS:	lib.texi

python-lib.info: lib.texi fix.el
	emacs -batch -l fix.el -f save-buffer -kill
	makeinfo --footnote-style end --fill-column 72 --paragraph-indent 0 \
	         lib.texi

lib.info: python-lib.info

# This target is very local to CWI...
libwww: lib.texi
	texi2html -d lib.texi /ufs/guido/www/texinfo/python

# This one too...
L2H=	/usr/local/LaTeX2html/latex2html
L2HARGS=-address $$USER@`domainname` -dont_include myformat -nolatex
l2h: l2htut l2href l2hext

l2htut: tut
	$(L2H) $(L2HARGS) tut.tex
	@rm -rf python-tut
	mv tut python-tut

l2href: ref
	$(L2H) $(L2HARGS) ref.tex
	@rm -rf python-ref
	mv ref python-ref

l2hext: ext
	$(L2H) $(L2HARGS) ext.tex
	@rm -rf python-ext
	mv ext python-ext

clean:
	rm -f @* *~ *.aux *.idx *.ilg *.ind *.log *.toc *.blg *.bbl *.pyc
	# Sources: .tex, .bib, .sty
	# Useful results: .dvi, .ps, .texi, .info

clobber: clean
	 rm -f *.dvi *.ps *.texi *.info *.info-[0-9]*
