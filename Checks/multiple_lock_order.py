import clang.cindex
from typing import List
from alerts import Alert
from Util import *
from formalCheckInterface import *

"""
A Check for the order of multiple locks. If found issue a warning.
"""

class Check(FormalCheckInterface):

    def __init__(self):
        self.check_init()

    def check_init(self):
        self.mutex_names = []
        self.heldLocks = list()
        self.usedLocks = list()
        self.scopeLevel = 0

    def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
        if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            if cursor.spelling == "lock":
                self.mutex_names.append(Lock(cursor).mutexName)
            elif cursor.spelling == "lock_guard":
                self.mutex_names.append(Lock_Guard(cursor, self.scopeLevel).mutexName)

        highestIndex = 0
        
        for mutex in self.mutex_names:
            if mutex in self.heldLocks:
                if mutex in self.usedLocks:
                    self.usedLocks.clear()
                    highestIndex = 0
                self.usedLocks.append(mutex)
                if (self.heldLocks.index(mutex) >= highestIndex):
                    highestIndex = self.heldLocks.index(mutex)
                else:
                    alerts.append(Alert(cursor.translation_unit, cursor.extent, "Error!: mutex " + str(mutex) + " is in the incorrect order!"))
            else:
                self.heldLocks.append(mutex)

        return alerts
