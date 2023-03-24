import clang.cindex
from typing import List
from alerts import Alert

"""
A Check for the order of multiple locks. If found issue a warning.
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list = list()
        heldLocks = list()
        usedLocks = list()
        mutex_names = []
        for match in cursor.get_children():
            if (str(match.displayname) == "std::lock_guard" and str(match.type.spelling) == "class std::mutex"):
                for c in match.get_children():
                    if (str(c.kind) == "CXX_MEMBER_CALL_EXPR" and str(c.spelling) == "lock"):
                        for a in c.get_children():
                            if (str(a.kind) == "DECL_REF_EXPR" and str(a.type.spelling) == "class std::mutex"):
                                mutex_names.append(a.spelling)
        multi_order = list(mutex_names)
        highestIndex = 0
        order_flag = 0
        for mutex in multi_order:
            if mutex in heldLocks:
                if mutex in usedLocks:
                    usedLocks.clear()
                highestIndex = 0
                usedLocks.append(mutex)
                if (heldLocks.index(mutex) >= highestIndex):
                    highestIndex = heldLocks.index(mutex)
                else:
                    order_flag = 1
                    alert_list.append(Alert(cursor.translation_unit, cursor.extent,
                                        "Error!: mutex " + str(mutex) + " is in the incorrect order!\n"))
            else:
                heldLocks.append(mutex)
        if order_flag == 0:
            alert_list.append(Alert(cursor.translation_unit, cursor.extent,
                                        "No lock order errors detected!\n"))
        return alert_list