import clang.cindex
from typing import List
from alerts import Alert

"""
TODO Write Description
"""
# We only want to run the check once!
checked = False

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list = list()
        global checked
        
        

        # If we haven't run the check before...
        if (not checked):
            joinDetected = 0
            joinableDetected = 0

            for node in  cursor.translation_unit.cursor.walk_preorder():
                            if node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "join" and node.type.spelling == "void": 
                               joinDetected += 1
                               #print("Found std::thread::join() function call at line {0}".format(node.location.line))
                            elif (node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "joinable" and node.type.spelling == "bool"):
                               joinableDetected += 1
                               #print("Found std::thread::joinable() function call at line {0}".format(node.location.line))


            if joinDetected != joinableDetected:
                 alert_list.append(Alert(cursor.translation_unit, cursor.extent,"Not all join functions are checked if thread is joinable"))

                             # Set the 'checked' flag, so we don't run this check again.
            checked = True

        return alert_list