;
; This turing machine subtracts two numbers; both numbers are given as
; a sequence of a's.
;
;
; The expected form is
;
;    n1,n2
;
; The result will be n1-n2, or zero if n1 < n2.
; The tape head will point to the result on return
;

<1, 'a'> --> <2, ' '>	; subtract one initially
<1, ','> --> <0, L>	; n2 bigger than n1, point to empty string (' ')

<2, ' '> --> <2, R>	; skip whitespace
<2, 'a'> --> <2, R>	; and the initial argument
<2, ','> --> <3, R>	; now we point to 2nd argument

<3, '#'> --> <3, R>	; skip past old arguments
<3, 'a'> --> <4, '#'>	; decrement 2nd argument
<3, ' '> --> <5, L>	; end of input

<4, '#'> --> <4, L>	; skip over the '#' characters
<4, ','> --> <4, L>	; and the delimiter
<4, 'a'> --> <4, L>	; and the 1st argument
<4, ' '> --> <1, R>	; point to first 'a' and change state

<5, '#'> --> <5, L>	; skip over the '#' characters
<5, ','> --> <5, L>	; and the delimiter
<5, 'a'> --> <5, L>	; and the 1st argument
<5, ' '> --> <0, 'a'>	; insert the a that we initially removed
