# Gráinne Ready

# SIDENOTE: If you think of any edge cases to test this with, or ways that I can improve the code, pls let me know! :)
# SIDENOTE: Call the 'def checkIfMembersLockedInSomeMethods(file_path : str):' function to check for the anti-pattern
# TODO: Add Scope handling
# TODO: Add handling for manual locks/unlocks

from output import *
from observer import *
import clang.cindex



class lockedInSomeObserver(Observer):
    
    def __init__(self):
        """
        Initialiser, Creates an instance of the lockedInSomeObserver class

        Args:
            None

        Returns:
            None
        """
        self.classes = []
        self.foundErrors = False
        self.errors = ""


    def update(self, currentNode : clang.cindex.Cursor):
        """Updates the lockedInSomeObserver with the current Node in the AST

        Args:
            currentNode (clang.cindex.Cursor): A node from the AST
        
        Returns:
            None
        
        Detailed Description:
            Updates the lockedInSomeObserver with the currentNode. If the node is a class (aka if it is of kind clang.cindex.cursorKind.CLASS_DECL) then
            it will gather all the methods and data members.
            Then, it will run through and see where locks are inside these methods. 
            If a data member is within a lock_guard's scope in one method, but is not within a lock_guard's scope in another, 
              it will raise an error about the data member, which will then be printed to the terminal
        """
        if currentNode not in self.classes:
            if currentNode.kind == clang.cindex.CursorKind.CLASS_DECL:
                self.classes.append(currentNode)

                # variables_under_lock is what we'll use to keep track of which variables are accessed in a lock_guard and which aren't
                #    key = data member node (clang.cindex.Cursor), 
                #    value = Was the data member accessed in a lock or not (bool)
                #    Because if we go to change it from True -> False or False -> True, then we know that it is accessed both in a lock_guard and outside a lock_guard (ERROR CASE)
                variables_under_lock = {}
                methods, class_variables = getMembersInClass(currentNode)
                for method in methods:
                    locks, method_variables = findLocksAndVariablesInMethod(method, class_variables)
                    for method_variable in method_variables:
                        if any(lock.lock_token.extent.start.line < method_variable.extent.start.line for lock in locks):
                            if method_variable.spelling in variables_under_lock and not variables_under_lock[method_variable.spelling]:
                                self.raiseError(method, method_variable, isLockedInMethod=True)
                            variables_under_lock[method_variable.spelling] = True
                        else:
                            if method_variable.spelling in variables_under_lock and variables_under_lock[method_variable.spelling]:
                                self.raiseError(method, method_variable, isLockedInMethod=False)
                            variables_under_lock[method_variable.spelling] = False


    def raiseError(self, methodNode : clang.cindex.Cursor, memberToken : clang.cindex.Token, isLockedInMethod : bool):
        """
        Raises an error, indicating that a data member is locked in some, but not all methods
        
        Args:
            methodNode (clang.cindex.Cursor): The node which represents the declaration of the method that the error-causing data member is inside of
            memberNode (clang.cindex.Cursor): The node which represents the data member inside the method which is locked in some, but not all methods
            isLockedInMethod (bool): A boolean which indicates whether the member was under lock or not in the specific method (This adjusts the error message)
        
        Returns:
            None
        """
        if (isLockedInMethod):
            print_error(memberToken._tu, methodNode.extent, 
                f"Data member '{memberToken.spelling}' is accessed with a lock_guard in this method, "+
                f"but is accessed without a lock_guard in other methods\n "+
                f"Are you missing a lock_guard in other methods which use '{memberToken.spelling}'?", "error")
            self.errors += f"""Data member '{methodNode.spelling}' is accessed with a lock_guard in this method,
but is accessed without a lock_guard in other methods
 Are you missing a lock_guard in other methods which use '{methodNode.spelling}'?"""
 
        else:
            print_error(memberToken._tu, methodNode.extent, 
                f"Data member '{memberToken.spelling}' is accessed without a lock_guard in this method, "+
                f"but is accessed with a lock_guard in other methods\n "+
                f"Are you missing a lock_guard before '{memberToken.spelling}'?", "error")
            self.errors += f"""Data member '{memberToken.spelling}' is accessed without a lock_guard in this method,
but is accessed with a lock_guard in other methods
 Are you missing a lock_guard before '{memberToken.spelling}'?"""

        self.foundErrors = True


# MAIN FUNCTION FOR THIS ANTI-PATTERN
# Gráinne Ready
        """
        Checks for 'data members locked in some, but not all methods' antipattern
        
        Args:
            file_path (str): The path of the c++ file to check for the antipattern
        
        Returns:
            errors (str): If there were instances of the antipattern detected in the file
            "PASSED - For data members locked in some, but not all methods" (str): If there were no errors detected
        """
def checkIfMembersLockedInSomeMethods(file_path : str):
    eventSrc = EventSource()
    locked_in_some_observer = lockedInSomeObserver()
    compound_statement_observer = CompoundStatementObserver()
    eventSrc.addMultipleObservers([locked_in_some_observer, compound_statement_observer])
    searchNodes(file_path, eventSrc)
    if locked_in_some_observer.foundErrors:
        return locked_in_some_observer.errors
    return "PASSED - For data members locked in some but not all methods"


# Gráinne Ready
    """
    Searches through every node in a c++ file (AST) and notifies Observers in the EventSource about it
    
    Args:
        file_path (str): The path of the c++ file to check for the antipattern
        eventSrc (EventSource): The EventSource object to notify observer with
    
    Returns:
        None
    """
def searchNodes(file_path : str, eventSrc: EventSource):
    index = clang.cindex.Index.create()
    tu = index.parse(file_path)

    for cursor in tu.cursor.walk_preorder():
        if(str(cursor.translation_unit.spelling) == str(cursor.location.file)):
            eventSrc.notifyObservers(cursor)


# Gráinne Ready
    """Gets all the cursors which are data members and methods, which are the children of a class and returns them in two separate lists
    
    Args:
        classCursor (clang.cindex.Cursor): A cursor of kind 'clang.cindex.CursorKind.CLASS_DECL'
    
    Returns:
        methods (list of clang.cindex.Cursor): A list of cursors which represent the methods of the class
        data_members (list of clang.cindex.Cursor): A list of cursors which represent the data members of the class (class variables)
    """
def getMembersInClass(classCursor : clang.cindex.Cursor):
    data_members = []
    method_names = []
    for child in classCursor.get_children():
        if child.kind == clang.cindex.CursorKind.CXX_METHOD:
            method_names.append(child)
        elif child.kind == clang.cindex.CursorKind.FIELD_DECL:
            data_members.append(child)
    return method_names, data_members


# Gráinne Ready
    """
    Gets all the cursors which are locks and variables of a method, and returns them in two separate lists
    
    Args:
        methodCursor (clang.cindex.Cursor): A cursor of kind 'clang.cindex.CXX_METHOD' which is a member of a class
        class_variables (list of clang.cindex.Cursor): A list of all data members of the class the method is inside of
    
    Returns:
        lock_guards (list of lock_guard): A list of lock_guards found in the method
        method_variables (list of clang.cindex.Token): A list of the class' data members which were used in the method
    """


def findLocksAndVariablesInMethod(methodCursor : clang.cindex.Cursor, class_variables):
    """
    Gets all the cursors which are locks and variables of a method, and returns them in two separate lists
    
    Args:
        methodCursor (clang.cindex.Cursor): A cursor of kind 'clang.cindex.CXX_METHOD' which is a member of a class
        class_variables (list of clang.cindex.Cursor): A list of all data members of the class the method is inside of
    
    Returns:
        lock_guards (list of lock_guard): A list of lock_guards found in the method
        method_variables (list of clang.cindex.Token): A list of the class' data members which were used in the method
    """
    method_variables = []
    lock_guards = []
    for child in methodCursor.get_children():
        if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            for token in child.get_tokens():
                for variable in class_variables:
                    if token.spelling == variable.spelling:
                        method_variables.append(token)
                if token.kind == clang.cindex.TokenKind.IDENTIFIER:
                    if token.spelling == "lock_guard":
                        lock_guards.append(lock_guard(token, None, None))
                    elif len(lock_guards) > 0:
                        if (lock_guards[-1].lock_name is None or lock_guards[-1].mutex_name is None):
                            checkIfPartOfLockedGuard(token, lock_guards[-1])
    return lock_guards, method_variables

# Grainne Ready
def checkIfPartOfLockedGuard(token : clang.cindex.Token, lock_grd : lock_guard):
    """Will check if a specific token is part of a line which declares a lock_guard

    Args:
        token (clang.cindex.Token): The token to check
        lock_grd (lock_guard): The lock_guard object to check if the token is a part of

    Returns:
        None
       
    """
    if lock_grd.lock_name is None:
        if (token.location.column - 23 == lock_grd.lock_token.location.column and token.location.line == lock_grd.lock_token.location.line):
            lock_grd.setLockName(token)
    elif lock_grd.mutex_name is None:
        if (token.location.column - 28 == lock_grd.lock_token.location.column and token.location.line == lock_grd.lock_token.location.line):
            lock_grd.setMutexName(token)