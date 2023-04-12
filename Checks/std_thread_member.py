import clang
import clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import FormalCheckInterface

"""
Check if each thread that exists in a class is joined/detached in the destructor
"""

threads = []

class Check(FormalCheckInterface):
    def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
        destructor = None

        # Check if a cursor is a class declaration
        if clang.cindex.CursorKind.CLASS_DECL == cursor.kind:

            # If it is we go over all its children to find its members and a destructor (if it exists)
            for cursorChild in cursor.get_children():
                if clang.cindex.CursorKind.FIELD_DECL == cursorChild.kind and "std::thread" in cursorChild.type.spelling:
                    threads.append(cursorChild)
                if clang.cindex.CursorKind.DESTRUCTOR == cursorChild.kind:
                    destructor = cursorChild

            if destructor is not None and len(threads) != 0:
                # Check destructor for detaching/joining of threads
                traverseDestructor(destructor)

            # Append alerts of all threads that aren't detatched/joined to the alert list
            for thread in threads:
                newAlert = Alert(thread.translation_unit, thread.extent,
                                 "Are you sure you want to have a thread called " + str(
                                     thread.displayname) + " without joining or detaching it in destructor?\n")
                destructor = None
                if newAlert not in alerts:
                    alerts.append(newAlert)

            threads.clear()


# Iterate the destructor and check if each thread detached/joined
def traverseDestructor(cursor: clang.cindex.Cursor):
    c: clang.cindex.Cursor
    for c in cursor.get_children():

        if str(cursor.translation_unit.spelling) == str(c.location.file):

            # We look for joining or detaching of a thread
            if str(c.displayname) == "join":
                traversejoinOrDetach(c)

            if str(c.displayname) == "detach":
                traversejoinOrDetach(c)

        traverseDestructor(c)  # Recursively traverse the tree.


# Iterate the join/detach cursor to find the name of the thread
def traversejoinOrDetach(cursor: clang.cindex.Cursor):
    c: clang.cindex.Cursor
    for c in cursor.get_children():

        if str(cursor.translation_unit.spelling) == str(c.location.file):

            # If the joining/detaching concerns one of the threads we remove it from the thread list
            for thread in threads:
                if str(c.displayname) == str(thread.displayname):
                    threads.remove(thread)

        traversejoinOrDetach(c)
