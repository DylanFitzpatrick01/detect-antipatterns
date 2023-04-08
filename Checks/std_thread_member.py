import clang
import clang.cindex
from typing import List
from alerts import Alert

threads = []

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list = list()

        destructor = None

        if clang.cindex.CursorKind.CLASS_DECL == cursor.kind:
            for cursorChild in cursor.get_children():
                if clang.cindex.CursorKind.FIELD_DECL == cursorChild.kind and "std::thread" in cursorChild.type.spelling:
                    threads.append(cursorChild)
                if clang.cindex.CursorKind.DESTRUCTOR == cursorChild.kind:
                    destructor = cursorChild

            if destructor is not None:
                #print("\nThreads Detected")
                for thread in threads:
                    print(str(thread.displayname))
                traverseDestructor(destructor)
                #print("\nThreads not joined or detached in Destructor")
            for thread in threads:
                #print(str(thread.displayname))
                alert_list.append(Alert(thread.translation_unit, thread.extent, "Are you sure you want to have a thread called " + str(thread.displayname) +" without joining or detaching it in destructor?\n"))
            threads.clear()

        return alert_list


def traverseDestructor(cursor: clang.cindex.Cursor):
    c: clang.cindex.Cursor
    for c in cursor.get_children():

        if str(cursor.translation_unit.spelling) == str(c.location.file):

            if str(c.displayname) == "join":
                #print("join detected")
                traversejoinOrDetach(c)

            if str(c.displayname) == "detach":
                #print("detach detected")
                traversejoinOrDetach(c)

        traverseDestructor(c)  # Recursively traverse the tree.

def traversejoinOrDetach(cursor: clang.cindex.Cursor):
    c: clang.cindex.Cursor
    for c in cursor.get_children():

        if str(cursor.translation_unit.spelling) == str(c.location.file):
            for thread in threads:
                if str(c.displayname) == str(thread.displayname):
                    threads.remove(thread)

        traversejoinOrDetach(c)


