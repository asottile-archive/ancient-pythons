;  From: heim@tub.UUCP (Heiner Marxen)
;  Newsgroups: sci.math
;  Subject: busy beaver Turing machine
;  Date: 24 Aug 89 13:24:10 GMT
;  Organization: Technical University of Berlin, Germany
;  
;  This is about ``busy beavers'' (is there a more appropriate newsgroup?).
;  Unfortunately I did read this newsgroup only sporadically, and don't know
;  whether this has been discussed already.  My other sources of information
;  (mainly the German issue of `Scientific American') don't tell me more.
;  
;  As far as I know the 5-state busy beaver question is not yet settled.
;  With the help of a program I have found a 5-state Turing machine which
;  halts (after 11,798,826 steps) and produces 4098 ones on the tape, namely
;      A0 -> B1L    A1 -> A1L             // `A' is the initial state
;      B0 -> C1R    B1 -> B1R             // `R' is `move right'
;      C0 -> A1L    C1 -> D1R             // `L' is `move left'
;      D0 -> A1L    D1 -> E1R
;      E0 -> H1R    E1 -> C0R             // `H' is the halting state
;  The best machine I knew before produces 1915 ones (published in 1985
;  by Scientific American, I believe).  My questions are
;   Q1: Is there ongoing (or completed) research ?  Any (theoretic) results ?
;   Q2: Are there any better 5-state machines known or published ?
;   Q3: Who else studies the busy beaver problem with general purpose computers?
;  
;  Answers to the above, hints and pointers are welcome.
;  Please answer by e-mail; If appropriate I will summarize to the net.
;  = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
;  Heiner Marxen,		from europe:	unido!tub!heim
;  				from world:	pyramid!tub!heim
;  				bitnet:		heim%tub.BITNET@mitvma.MIT.EDU

<1, ' '> --> <2, 'a'>
<1, 'a'> --> <1, L>
<2, 'a'> --> <3, L>

<3, ' '> --> <4, 'a'>
<3, 'a'> --> <3, R>
<4, 'a'> --> <5, R>

<5, ' '> --> <6, 'a'>
<5, 'a'> --> <7, R>
<6, 'a'> --> <1, L>

<7, ' '> --> <8, 'a'>
<7, 'a'> --> <9, R>
<8, 'a'> --> <1, L>

<9, ' '> --> <10, 'a'>
<9, 'a'> --> <11, ' '>
<10, 'a'> --> <0, R>
<11, ' '> --> <5, R>
