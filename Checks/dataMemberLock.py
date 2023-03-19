import clang.cindex
from typing import List
from alerts import Alert

"""
TODO Detect issues with data member that is accessed under a lock, but is also public so can be read/written directly. 
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list: List[Alert] = list()

        #code
        
        return alert_list
        
    