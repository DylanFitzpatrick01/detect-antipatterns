# Gráinne Ready

# SIDENOTE: If you think of any edge cases to test this with, or ways that I can improve the code, pls let me know! :)
# SIDENOTE: Call the 'def checkIfMembersLockedInSomeMethods(file_path : str):' function to check for the anti-pattern
# TODO: Add handling for nested methods (e.g. calculate() in order.cpp gives a false error)
# TODO: Add handling for if-else statements, do-while loops, while-loops etc.. (LOT of this to do, at the moment these can pass when they shouldn't)

from output import *
from observer import *
import clang.cindex

# Gráinne Ready
# Looks for a node that is a class declaration, and then checks if there are class variables that are lock_guarded in some, but not all, of the class' methods
class lockedInSomeObserver(Observer):
    def __init__(self, translationUnit):
        self.classes = []
        self.foundErrors = False
        self.output = ""


    def update(self, currentNode):
        if currentNode not in self.classes:
            if currentNode.kind == clang.cindex.CursorKind.CLASS_DECL:
                self.classes.append(currentNode)

                # variables_under_lock is what we'll use to keep track of which variables are accessed in a lock_guard and which aren't
                #    key = variableNode, value = True/False (Value: Was it accessed in a lock_guard or not)
                #    Because if we go to change it from True -> False or False -> True, then we know that it is accessed both in a lock_guard and outside a lock_guard (ERROR CASE)
                variables_under_lock = {}
                methods, class_variables = getMembersInClass(currentNode)
                for method in methods:
                    locks, method_variables = findLocksAndVariablesInMethod(method, class_variables)
                    for method_variable in method_variables:
                        if len(locks) > 0:
                            for lock in locks:
                                if lock.extent.start.line < method_variable.extent.start.line:
                                    if method_variable.displayname in variables_under_lock:
                                        if variables_under_lock[method_variable.displayname] == False:
                                            self.output += f"""Data member '{method_variable.displayname}' is accessed with a lock_guard in this method,
but is accessed without a lock_guard in other methods
 Are you missing a lock_guard in other methods which use '{method_variable.displayname}'?"""
                                            # At the moment, this error prints the function that contains the lock_guard. It might be better to make it print the functions which don't have a lock_guard
                                            print_error(method_variable.translation_unit, method.extent, 
                                                        f"Data member '{method_variable.displayname}' is accessed with a lock_guard in this method, "+
                                                        f"but is accessed without a lock_guard in other methods\n "+
                                                        f"Are you missing a lock_guard in other methods which use '{method_variable.displayname}'?", "error")
                                            self.foundErrors = True
                                    else:
                                        variables_under_lock[method_variable.displayname] = True
                        else:
                            if method_variable.displayname in variables_under_lock:
                                if variables_under_lock[method_variable.displayname] == True:
                                    self.output += f"""Data member '{method_variable.displayname}' is accessed without a lock_guard in this method,
but is accessed with a lock_guard in other methods
 Are you missing a lock_guard before '{method_variable.displayname}'?"""
                                    print_error(method_variable.translation_unit, method.extent, 
                                                f"Data member '{method_variable.displayname}' is accessed without a lock_guard in this method, "+
                                                f"but is accessed with a lock_guard in other methods\n "+
                                                f"Are you missing a lock_guard before '{method_variable.displayname}'?", "error")
                                    self.foundErrors = True
                            else:
                                variables_under_lock[method_variable.displayname] = False
                if (not self.foundErrors):
                    self.output += "PASSED - For data members locked in some but not all methods"
                    print("PASSED - For data members locked in some but not all methods")


# MAIN FUNCTION FOR THIS ANTI-PATTERN
# Gráinne Ready
# Will run through a c++ file and check if data members in the file are lock_guarded in some, but not all methods
# If a data member is in a lock_guarded method, but is also in a method without a lock_guard,
#    then an error is printed to the terminal which includes the name of the data member, and the scope of the method the data member is in
# Else, it will print out 'PASSED TEST - For data members locked in some but not all methods'
# @Param file_path: The path of the c++ file to check
# @Return locked_in_some_observer.output: The output of the observer which checks for the antipattern (Output is also printed to terminal)
def checkIfMembersLockedInSomeMethods(file_path : str):
    eventSrc = EventSource()
    locked_in_some_observer = lockedInSomeObserver(clang.cindex.Index.create().parse(file_path))
    eventSrc.addObserver(locked_in_some_observer)
    searchNodes(file_path, eventSrc)
    return locked_in_some_observer.output
        
    
# Gráinne Ready
# Searches through every node in a c++ file and notifies the Observers about it
# @Param file_path:     The file path of the c++ file to search through
# @Param eventSrc:      The EventSource() object that notifies the observers   
def searchNodes(file_path, eventSrc: EventSource):
    index = clang.cindex.Index.create()
    tu = index.parse(file_path)

    for cursor in tu.cursor.walk_preorder():
        if(str(cursor.translation_unit.spelling) == str(cursor.location.file)):
            eventSrc.notifyObservers(cursor)


# Gráinne Ready
# Gets all the cursors which are data members and member functions, that are the children of a class and returns them in two separate lists
# @Param classCursor:   A cursor of kind 'clang.cindex.CursorKind.CLASS_DECL'
# @Returns methods:     A list of the member functions which are of kind 'clang.cindex.CursorKind.CXX_METHOD'
# @Returns variables:   A list of the data members which are of kind 'clang.cindex.CursorKind.FIELD_DECL'
def getMembersInClass(classCursor):
    variables = []
    methods = []
    for child in classCursor.get_children():
        if child.kind == clang.cindex.CursorKind.CXX_METHOD:
            methods.append(child)
        elif child.kind == clang.cindex.CursorKind.FIELD_DECL:
            variables.append(child)
    return methods, variables


# Gráinne Ready
# Given a cursor that is a method declaration, and a list of all class variables that are in the class the member belongs to,
# this will return a list of all locks that are in the method, and a list of all the class_variables used in the method
# @Param methodCursor:          A cursor of kind 'clang.cindex.CursorKind.CXX_METHOD'
# @Param class_variables:       A list of all variables belonging to the class that the method is in
# @Returns locks:               A list of all locks found in the method
# @Returns method_variables:    A list of all class_variables found in the method
def findLocksAndVariablesInMethod(methodCursor, class_variables):
    locks = []
    method_variables = []
    for child in methodCursor.walk_preorder():
        for variable in class_variables:
            if child.spelling == variable.spelling and child.type.spelling == variable.type.spelling:
                method_variables.append(child)
        if child.kind == clang.cindex.CursorKind.CALL_EXPR and child.spelling == "lock_guard":
            locks.append(child)
    return locks, method_variables


# *******NOT USED*******
# Gráinne Ready
# Given a cursor that is a class declaration, it will search through the children of the cursor for all methods in that class,
#   and return a list of all method cursors that are children of that class
# @Param classCursor:   A cursor of kind 'clang.cindex.CursorKind.CLASS_DECL
# @Returns methodsList: A list of cursors which are of kind 'clang.cindex.CursorKind.CXX_METHOD' that are children of the class
def getMethodsInClass(classCursor):
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
def getVariablesInClass(classCursor):
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
def getLockGuardsInMethod(methodCursor):
    locks = [] 
    for child in methodCursor.walk_preorder():
        if child.kind == clang.cindex.CursorKind.CALL_EXPR and child.spelling == "lock_guard":
            locks.append(child)
    return locks


if __name__ == "__main__":
    checkIfMembersLockedInSomeMethods("err_lock_in_some_methods.cpp")