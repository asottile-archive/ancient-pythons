;
; Decrement a number.  This is easy.
; The tape head points to the output.
;

<1, 'a'> --> <2, ' '>	; decrement a sequence of a's
<1, ' '> --> <0, L>	; decrement zero

<1, 'S'> --> <2, ' '>	; decrement SSSS....SSSS0
<1, '0'> --> <0, L>	; decrement zero

<2, ' '> --> <0, R>	; move tape head right one before halting
