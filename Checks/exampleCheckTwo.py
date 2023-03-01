from Core.formalCheckInterface import *

"""
A Check for a different antipattern! analyse_cursor() runs for EVERY cursor!
"""

class Check(FormalCheckInterface):
    def analyse_cursor(self, cursor: clang.cindex.Cursor):
        alert_list: List[Alert] = list()
        
        return alert_list