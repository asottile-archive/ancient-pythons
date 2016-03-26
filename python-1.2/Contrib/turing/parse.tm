
;
; This turing machine will accept any inputs of the form 0...01...1, where
; there are an equal number of zeros and ones and will reject all other
; inputs.
;
; on return, the tape head will point to the character 'Y' if it accepts,
; and the character 'N' if it rejects.
;

<1, '0'> --> <1, '!'>	; replace zero on the left
<1, '1'> --> <0, 'N'>	; 1 when first digit must be zero, reject
<1, '!'> --> <2, R>	; find the first 1

<2, '0'> --> <2, R>	; skip other zero's
<2, '1'> --> <3, R>	; go to the rightmost 1.
<2, ' '> --> <0, 'N'>	; Didn't find a 1, don't accept
<2, '%'> --> <0, 'N'>	; ditto for this case

<3, '1'> --> <3, R>	; Skip one's
<3, '0'> --> <0, 'N'>	; found a 0 mixed in, don't accept
<3, '%'> --> <4, L>	; at the rightmost 1.
<3, ' '> --> <4, L>	; ditto

<4, '1'> --> <4, '%'>	; replace the one
<4, '%'> --> <5, L>	; and move to find a zero

<5, '1'> --> <5, L>	; find leftmost zero
<5, '0'> --> <5, L>	; found the zero's...
<5, '!'> --> <6, R>	; in state <6> we are at the leftmost zero

<6, '0'> --> <1, '!'>	; replace with '!' and repeat
<6, '1'> --> <0, 'N'>	; some one's are left
<6, '%'> --> <0, 'Y'>	; all one's are consumed
