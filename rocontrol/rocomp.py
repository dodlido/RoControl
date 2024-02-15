from typing import Tuple

EQ   = '='
NEQ  = '!='
LEQ  = '<='
LNEQ = '<'
GEQ  = '>='
GNEQ = '>'

def comp_inv(comp: str) -> str:
    if (comp==EQ):
        return NEQ
    elif (comp==NEQ):
        return EQ
    elif (comp==LEQ):
        return GNEQ
    elif (comp==LNEQ):
        return GEQ
    elif (comp==GEQ):
        return LNEQ
    elif (comp==GNEQ):
        return LEQ
    else:
        print('Err: failed inversion, comperator not found')
        exit(2)

def find_comp(some_str: str) -> Tuple[int, str]:
    comp_list = [NEQ, LEQ, LNEQ, GEQ, GNEQ, EQ]
    for c in comp_list:
        ind = some_str.find(c)
        if ind!=-1:
            return ind, c
    return -1, ''

