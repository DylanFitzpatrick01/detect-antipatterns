from Core.formalCheckInterface import *
from typing import List

"""
A Check for a different antipattern! analyse_cursor() runs for EVERY cursor!
"""

class Check(FormalCheckInterface):
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list: List[Alert] = list()
        
        return alert_list