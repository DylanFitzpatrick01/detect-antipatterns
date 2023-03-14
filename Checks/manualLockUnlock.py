import clang.cindex
from alerts import Alert

"""
A Check for a manual lock/unlock. If found issue a warning.
HOWEVER!! if we find a lock without an unlock, issue an error.#
Analyse_cursor() runs for EVERY cursor.
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor):
        alert_list = list()

        if (cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT):
            lock_caller = find_caller(cursor, "lock")
            unlock_caller = find_caller(cursor, "unlock")
            if (lock_caller and unlock_caller):
                alert_list.append(Alert(cursor.translation_unit, cursor.extent,
                                        "A manual lock/unlock is used in this scope.\n" 
                                        "It's reccommended you use an RAII locking scheme, i.e.\n"
                                        "remove '" + lock_caller + ".unlock();' and replace '" + lock_caller + ".lock();' with\n"
                                        "'std::lock_guard<std::mutex> lock(" + lock_caller + ");'", "warning"))
            if (lock_caller and not unlock_caller):
                alert_list.append(Alert(cursor.translation_unit, cursor.extent,
                                        "A manual lock is used in this scope without an unlock!.\n"
                                        "Please either replace '" + lock_caller + ".lock();' with 'std::lock_guard<std::mutex> lock(" + lock_caller + ");' (RECCOMMENDED),\n"
                                        "or add '" + lock_caller + ".unlock();' at the end of this critical section."))
        
        return alert_list
    
                                 

# Given a function name 'func', if "class.func()" is found, return class.
def find_caller(cursor:clang.cindex.Cursor, name):
    toks = list(cursor.get_tokens())
    for i in range (len(toks)):
        if(toks[i].spelling == name and toks[i-1].spelling == "."):
            return toks[i-2].spelling