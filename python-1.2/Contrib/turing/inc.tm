<1, 'a'> --> <1, R>	; Given a number as a sequences of a's increase it
<1, ' '> --> <0, 'a'>	; by one

<1, 'S'> --> <1, R>	; given a number of the form SSSSS...SSS0
<1, '0'> --> <2, 'S'>	; add another S
<2, 'S'> --> <2, R>	; go right one
<2, ' '> --> <0, '0'>	; append the zero
