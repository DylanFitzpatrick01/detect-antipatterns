import clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import *

"""
Detect public mutex members 
"""

# Check if a cursor is a public std::mutex
class Check(FormalCheckInterface):
    def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):

        # Check if cursor is public
        if str(cursor.access_specifier) == "AccessSpecifier.PUBLIC":
            count = 0
            contains = False

            # Iterate over all cursor children
            for cursor1 in cursor.get_children():
                count += 1

                # Check if any of the children is of std::mutex type
                if str(cursor1.displayname) == "class std::mutex" and str(cursor1.kind) == "CursorKind.TYPE_REF":
                    contains = True
                if count > 2:
                    break

            # Create new alert and add to the alert list
            if contains and count == 2:
                newAlert = Alert(cursor.translation_unit, cursor.extent,
                                 "Are you sure you want to have a public mutex called '" + cursor.displayname + "'?\n"
                                                                                                                "Consider making this mutex private.")

                if newAlert not in alerts:
                    alerts.append(newAlert)
