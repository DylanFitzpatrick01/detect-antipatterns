import clang.cindex
from typing import List
from alerts import Alert

"""
TODO Write Description
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list = list()

        i