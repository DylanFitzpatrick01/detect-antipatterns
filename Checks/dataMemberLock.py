import clang.cindex
from typing import List
from alerts import Alert

"""
TODO Detect issues with data member that is accessed under a lock, but is also public so can be read/written directly. 
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        # alert_list: List[Alert] = list()
        alert_list = list()

        #code

        #print(f"{cursor.kind} at:\t({cursor.extent.start.line}, {cursor.extent.start.column})-({cursor.extent.end.line}, {cursor.extent.end.column})")
        
        if (cursor.kind == clang.cindex.CursorKind.FIELD_DECL and cursor.access_specifier == clang.cindex.AccessSpecifier.PUBLIC):
            


        # if str(cursor.access_specifier) == "AccessSpecifier.PUBLIC":
        #     #print(cursor.access_specifier)
        #     count = 0
        #     contains = False
        #     for cursor1 in cursor.get_children():
        #         count+= 1
        #         if str(cursor1.displayname) == "std::mutex" and str(cursor1.kind) == "CursorKind.TYPE_REF":
        #             contains = True
        #         if count > 2:
        #             break
        #         if contains and count == 2:
        #             # alert_list.apend(Alert(cursor.translation_unit, cursor.extent, "Are you sure you want to habe a public member called '" + cursor.displayname + "'?\n"
        #             #                            "Consider making this mutex private"))
        #             print("Are you sure you want to habe a public member called '" + cursor.displayname + "'?\n")
                                     
            print(f"{cursor.kind} at:\t({cursor.extent.start.line}, {cursor.extent.start.column})-({cursor.extent.end.line}, {cursor.extent.end.column})")
            print("Are you sure you want a public member called '" +cursor.displayname+ "' consider making this data member private")
        
        if str(cursor.access_specifier) == "AccessSpecifier.PUBLIC":
                count = 0
                contains = False
                for cursor1 in cursor.get_children():
                    count += 1
                    if str(cursor1.displayname) != "class std::mutex" and str(cursor1.kind) == "CursorKind.TYPE_REF":
                        contains = True
                    if count > 2:
                        break
                if contains and count == 2:
                    alert_list.append(Alert(cursor.translation_unit, cursor.extent,
                                            "Are you sure you want to have a public mutex called '" + cursor.displayname + "'?\n"
                                            "Consider making this mutex private."))
        
        return alert_list