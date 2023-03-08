# Gráinne Ready

# SIDENOTE: If you think of any edge cases to test this with, or ways that I can improve the code, pls let me know! :)
# SIDENOTE: Call the 'def checkIfMembersLockedInSomeMethods(file_path : str):' function to check for the anti-pattern
# TODO: Add handling for manual locks/unlocks
# TODO: Add handling for nested methods (e.g. calculate() in order.cpp gives a false error)
# TODO: Add handling for if-else statements, do-while loops, while-loops etc.. (LOT of this to do, at the moment these can pass when they shouldn't)

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
                        if any(lock.extent.start.line < method_variable.extent.start.line for lock in locks):
                            if method_variable.displayname in variables_under_lock and not variables_under_lock[method_variable.displayname]:
                                self.raiseError(method, method_variable, isLockedInMethod=True)
                            variables_under_lock[method_variable.displayname] = True
                        else:
                            if method_variable.displayname in variables_under_lock and variables_under_lock[method_variable.displayname]:
                                self.raiseError(method, method_variable, isLockedInMethod=False)
                            variables_under_lock[method_variable.displayname] = False


    def raiseError(self, methodNode : clang.cindex.Cursor, memberNode : clang.cindex.Cursor, isLockedInMethod : bool):
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
            print_error(memberNode.translation_unit, methodNode.extent, 
                f"Data member '{memberNode.displayname}' is accessed with a lock_guard in this method, "+
                f"but is accessed without a lock_guard in other methods\n "+
                f"Are you missing a lock_guard in other methods which use '{memberNode.displayname}'?", "error")
            self.errors += f"""Data member '{methodNode.displayname}' is accessed with a lock_guard in this method,
but is accessed without a lock_guard in other methods
 Are you missing a lock_guard in other methods which use '{methodNode.displayname}'?"""
 
        else:
            print_error(memberNode.translation_unit, methodNode.extent, 
                f"Data member '{memberNode.displayname}' is accessed without a lock_guard in this method, "+
                f"but is accessed with a lock_guard in other methods\n "+
                f"Are you missing a lock_guard before '{memberNode.displayname}'?", "error")
            self.errors += f"""Data member '{memberNode.displayname}' is accessed without a lock_guard in this method,
but is accessed with a lock_guard in other methods
 Are you missing a lock_guard before '{memberNode.displayname}'?"""

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
    eventSrc.addObserver(locked_in_some_observer)
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
    methods = []
    for child in classCursor.get_children():
        if child.kind == clang.cindex.CursorKind.CXX_METHOD:
            methods.append(child)
        elif child.kind == clang.cindex.CursorKind.FIELD_DECL:
            data_members.append(child)
    return methods, data_members


# Gráinne Ready
    """
    Gets all the cursors which are locks and variables of a method, and returns them in two separate lists
    
    Args:
        methodCursor (clang.cindex.Cursor): A cursor of kind 'clang.cindex.CXX_METHOD' which is a member of a class
        class_variables (list of clang.cindex.Cursor): A list of all data members of the class the method is inside of
    
    Returns:
        locks (list of clang.cindex.Cursor): A list of lock_guards found in the method
        method_variables (list of clang.cindex.Cursor): A list of the class' data members which were used in the method
    """
def findLocksAndVariablesInMethod(methodCursor : clang.cindex.Cursor, class_variables):
    lock_guards = []
    locks = []
    unlocks = []
    lock_pairs = []
    method_variables = []

    for child in methodCursor.walk_preorder():
        for variable in class_variables:
            if child.spelling == variable.spelling and child.type.spelling == variable.type.spelling:
                method_variables.append(child)
        if child.kind == clang.cindex.CursorKind.CALL_EXPR and child.spelling == "lock_guard":
            lock_guards.append(child)
        elif child.spelling == "lock":
            locks.append(child)
        elif child.spelling == "unlock":
            unlocks.append(child)
    
    for lock in locks:
        for unlock in unlocks:
            if lock.semantic_parent == unlock.semantic_parent:
                lock_pairs.append((lock, unlock))
    return lock_guards, method_variables


# *******NOT USED*******
# Gráinne Ready
# Given a cursor that is a class declaration, it will search through the children of the cursor for all methods in that class,
#   and return a list of all method cursors that are children of that class
# @Param classCursor:   A cursor of kind 'clang.cindex.CursorKind.CLASS_DECL
# @Returns methodsList: A list of cursors which are of kind 'clang.cindex.CursorKind.CXX_METHOD' that are children of the class
def getMethodsInClass(classCursor : clang.cindex.Cursor):
    methodsList = []
    for child in classCursor.get_children():
        if child.kind == clang.cindex.CursorKind.CXX_METHOD:
            methodsList.append(child)
    return methodsList


# *******NOT USED*******
# Gráinne Ready
# Gets all variable cursors that are children of a class and returns them in a list
# @Param classCursor:   A cursor of kind 'clang.cindex.CursorKind.CLASS_DECL'
# @Returns variables:   A list of the variables found in the class
def getVariablesInClass(classCursor : clang.cindex.Cursor):
    variables = []
    for child in classCursor.get_children():
        if child.kind == clang.cindex.CursorKind.FIELD_DECL:
            variables.append(child)
    return variables


# *******NOT USED*******
# Gráinne Ready
# Given a cursor that is a method declaration, it will search through the method for lock_guards, and then return a list of the mutexes which are in lock_guards
# @Param methodCursor:      A cursor of kind 'clang.cindex.CursorKind.CXX_METHOD'
# @Returns guardedMutexes:  The list of all mutexes in the method
def getLockGuardsInMethod(methodCursor : clang.cindex.Cursor):
    lock_guards = [] 
    for child in methodCursor.walk_preorder():
        if child.kind == clang.cindex.CursorKind.CALL_EXPR and child.spelling == "lock_guard":
            lock_guards.append(child)
    return lock_guards


if __name__ == "__main__":
    checkIfMembersLockedInSomeMethods("err_lock_in_some_methods.cpp")