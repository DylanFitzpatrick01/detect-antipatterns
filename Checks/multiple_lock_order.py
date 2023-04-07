import clang.cindex
from typing import List
from alerts import Alert
import re

"""
A Check for the order of multiple locks. If found issue a warning.
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list = list()
        if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            function_name = cursor.spelling
            if function_name == "lock":
                mutex_names = []
                for child in cursor.get_children():
                    if child.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                        mutex_names.append(child.spelling)
                multi_order = list(mutex_names)
                heldLocks = list()
                usedLocks = list()
                highestIndex = 0
                for mutex in multi_order:
                    if mutex in heldLocks:
                        if mutex in usedLocks:
                            usedLocks.clear()
                        highestIndex = 0
                        usedLocks.append(mutex)
                        if (heldLocks.index(mutex) >= highestIndex):
                            highestIndex = heldLocks.index(mutex)
                        else:
                            alert_list.append(Alert(cursor.translation_unit, cursor.extent, "Error!: mutex " + str(mutex) + " is in the incorrect order!\n"))
                    else:
                        heldLocks.append(mutex)
        return alert_list
