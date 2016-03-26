#
# module match.py
#
# pattern matcher (unification without nested terms);
# see holmes/match.py and holmes.doc for more info;
##############################################################





def substitute(term, dict):
    if type(term) == type([]):
        res = []
        for x in term:
            res.append(substitute(x, dict))           # free vars = '?'
        return res
    else:
        return ground(term, dict)[0]                  # replace vars with vals





def ground(term, dict):
    if term[0] != '?':
        return term, ()                         # literal term

    else:
        name = term[1:]
        if not dict.has_key(name):
            dict[name] = '?'                    # add as free var now
            return '?', (name, dict)
        else:
            n, d = name, dict                   # follow binding chain
            while type(d[n]) == type(()):
                n, d = d[n]                     # ends in literal or free
            return d[n], (n, d)                 # return val + var





def match(term1, term2, dict1, dict2):
    if len(term1) != len(term2):                        # one list shorter
        return (0, [])
    
    else:
        bindings = []
        for i in range(len(term1)):                     
            g1, v1 = ground(term1[i], dict1)            # eval vars first
            g2, v2 = ground(term2[i], dict2)

            if g1 != '?' and g2 != '?':                 # both end in literals
                if g1 != g2:
                    return (0, bindings)                # must be same string
            else:
                if g2 != '?':                           # bind term1 to literal
                    v1[1][v1[0]] = g2                   # n, d = v1; d[n] = g2
                    bindings.append(v1)                 # record binding made       
                
                elif g1 != '?':                         # bind term2 to literal
                    v2[1][v2[0]] = g1                                 
                    bindings.append(v2)
                
                else:                                   # both ref free vars 
                    n1, d1 = v1                         # dont bind to self
                    n2, d2 = v2
                    if not (n1 == n2 and d1 is d2):
                        d2[n2] = v1                         
                        bindings.append(v2)             # cross-bind free vars
        
        return (1, bindings)
 

