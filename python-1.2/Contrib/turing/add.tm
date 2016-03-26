;
; This turing machine takes two sequences of a's and adds them together.
; The output is always at the start of the tape.

<1, 'a'> --> <1, R>
<1, ','> --> <2, 'a'>
<1, ' '> --> <0, ' '>
<2, 'a'> --> <2, R>
<2, ' '> --> <3, L>
<3, 'a'> --> <0, ' '>
