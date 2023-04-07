import clang.cindex
from typing import List
from alerts import Alert

"""
A Check for the order of multiple locks. If found issue a warning.
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list = list()
        mutex_names = []
        for child_cursor in cursor.get_children():
            if str(child_cursor.displayname) == "class std::mutex" and str(child_cursor.kind) == "CursorKind.TYPE_REF":
                mutex_names.append(child_cursor.displayname)
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
                    alert_list.append(Alert(child_cursor.translation_unit, child_cursor.extent, "Error!: mutex " + str(mutex) + " is in the incorrect order!\n"))
            else:
                heldLocks.append(mutex)
        return alert_list