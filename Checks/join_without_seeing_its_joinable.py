import clang.cindex
from typing import List
from alerts import Alert

"""
TODO Write Description
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list = list()
        joinDetected = 0
        joiableDetected = 0

        for node in  cursor.translation_unit.cursor.walk_preorder():
            if node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "join":
                               joinDetected =+ 1
            elif node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "joinable":
                joiableDetected =+1


        if joinDetected > joiableDetected:
             alert_list.append(Alert(cursor.translation_unit, cursor.extent,"Not all join functions check if thread is joinable",
                                     "\n Recommend adding a if( x.joinable) function"))