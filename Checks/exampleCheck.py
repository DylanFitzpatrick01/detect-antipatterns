from Core.formalCheckInterface import *
from typing import List

"""
A Check for some antipattern. analyse_cursor() runs for EVERY cursor!
"""

class Check(FormalCheckInterface):
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list: List[Alert] = list()

        if (cursor.location.line == 5):
            alert_list.append(Alert(cursor.translation_unit, cursor.extent, "Test!"))
        
        return alert_list
