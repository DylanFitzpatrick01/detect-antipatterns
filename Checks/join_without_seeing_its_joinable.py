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
        joinableDetected = 0

        for node in  cursor.translation_unit.cursor.walk_preorder():
                        if node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "join" and node.type.spelling == "void": 
                           joinDetected += 1
                           print("Found std::thread::join() function call at line {0}".format(node.location.line))
                        elif (node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "joinable" and node.type.spelling == "bool"):
                           joinableDetected += 1
                           #print("Found std::thread::joinable() function call at line {0}".format(node.location.line))


        if joinDetected > joinableDetected:
             alert_list.append(Alert(cursor.translation_unit, cursor.extent,"Not all join functions are checked if thread is joinable",
                                     "\n Recommend adding a if( x.joinable) function"))