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

        #print(f"{cursor.kind} at:\t({cursor.extent.start.line}, {cursor.extent.start.column})-({cursor.extent.end.line}, {cursor.extent.end.column})")
        
        if (cursor.kind == clang.cindex.CursorKind.FIELD_DECL and cursor.access_specifier == clang.cindex.AccessSpecifier.PUBLIC):
            #print(cursor.access_specifier)
            print(f"{cursor.kind} at:\t({cursor.extent.start.line}, {cursor.extent.start.column})-({cursor.extent.end.line}, {cursor.extent.end.column})")

            if():
                print()