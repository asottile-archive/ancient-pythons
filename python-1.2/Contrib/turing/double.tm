; This turing machine doubles its input.  Useful to check that dynamic
; strings work.  On output, the tape head will point to the result.
;

<1, 'a'> --> <1, '#'>
<1, '#'> --> <2, R>
<1, ' '> --> <0, R>

<2, 'a'> --> <2, R>
<2, ' '> --> <3, R>

<3, 'a'> --> <3, R>
<3, ' '> --> <4, 'a'>

<4, 'a'> --> <4, R>
<4, ' '> --> <5, 'a'>

<5, 'a'> --> <5, L>
<5, ' '> --> <5, L>
<5, '#'> --> <1, R>
