import clang.cindex
from cursorSearch import *
import sys

def isUnlockCalled(cursor:clang.cindex.Cursor, caller_name):
    # TODO, generalise from unlock to anything
    toks = list(cursor.get_tokens())
    for i in range (len(toks)):
        if(toks[i].spelling == "unlock"):
            if(toks[i-2].spelling == caller_name and toks[i-1].spelling == "." ):
                return True
            else:
                print(toks[i-2].spelling + toks[i-1].spelling + "unlock")
    return False


#Very simple method, make more clangy....
def findCaller(cursor:clang.cindex.Cursor, name):
    toks = list(cursor.get_tokens())
    for i in range (len(toks)):
        if(toks[i].spelling == name):
            return toks[i-2].spelling