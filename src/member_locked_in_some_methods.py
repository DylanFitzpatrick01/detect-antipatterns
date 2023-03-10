# Gráinne Ready

# SIDENOTE: If you think of any edge cases to test this with, or ways that I can improve the code, pls let me know! :)
# SIDENOTE: Call the 'def checkIfMembersLockedInSomeMethods(file_path : str):' function to check for the anti-pattern
# TODO: Test with c++ code that includes do-while loops, while-loops etc..
# TODO: Improve code - If I store the compound_statement of the class in lockedInSomeObserver, I could check when all the
#                      nodes in the class have been read. It may not seem like it on paper, but this would actually highly
#                      boost efficiency, as I could then make it so it only reads nodes once, as atm some nodes are read more
#                      than once since I use walk_preorder() in some functions. I would be able to remove those walks if I
#                      do this. This could take time, so I'd prefer to prioritise getting the other antipatterns first.
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
        if currentNode.kind == clang.cindex.CursorKind.CLASS_DECL:
            # variables_under_lock is what we'll use to keep track of which variables are accessed in a lock_guard and which aren't
            #    key = data member node (clang.cindex.Cursor), 
            #    value = Was the data member accessed in a lock or not (bool)
            #    Because if we go to change it from True -> False or False -> True, then we know that it is accessed both in a lock_guard and outside a lock_guard (ERROR CASE)
            variables_under_lock = {}
            methods, class_variables = getMembersInClass(currentNode)
            for method in methods:
                lock_scope_pairs, method_variables, lock_unlock_pairs = findLocksAndVariablesInMethod(method, class_variables)
                for method_variable in method_variables:
                    if any(lock[0].extent.start.line <= method_variable.extent.start.line and lock[1].extent.end.line >= method_variable.extent.end.line for lock in lock_scope_pairs):
                        if method_variable.displayname in variables_under_lock and not variables_under_lock[method_variable.displayname]:
                            self.raiseError(method, method_variable, isLockedInMethod=True)
                        variables_under_lock[method_variable.displayname] = True
                    elif any(lock_unlock_pair[0].extent.start.line <= method_variable.extent.start.line and lock_unlock_pair[2].extent.end.line >= method_variable.extent.end.line for lock_unlock_pair in lock_unlock_pairs):
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
                f"Data member '{memberNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is accessed with a lock_guard in this method, "+
                f"but is accessed without a lock_guard in other methods\n "+
                f"Are you missing a lock_guard in other methods which use '{memberNode.displayname}'?", "error")
            self.errors += f"""Data member '{methodNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is accessed with a lock_guard in this method,
but is accessed without a lock_guard in other methods
 Are you missing a lock_guard in other methods which use '{methodNode.displayname}'?"""
 
        else:
            print_error(memberNode.translation_unit, methodNode.extent, 
                f"Data member '{memberNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is accessed without a lock_guard in this method, "+
                f"but is accessed with a lock_guard in other methods\n "+
                f"Are you missing a lock_guard before '{memberNode.displayname}'?", "error")
            self.errors += f"""Data member '{memberNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is accessed without a lock_guard in this method,
but is accessed with a lock_guard in other methods
 Are you missing a lock_guard before '{memberNode.displayname}'?"""


# MAIN FUNCTION FOR THIS ANTI-PATTERN AT THE MOMENT
# Gráinne Ready
        """
        Checks for 'data members locked in some, but not all methods' antipattern
        
        Args:
            file_path (str): The path of the c++ file to check for the antipattern
        
        Returns:
            errors (str): Information about the errors found, if there were instances of the antipattern detected in the file
            "PASSED - For data members locked in some, but not all methods" (str): If there were no errors detected
        """
def checkIfMembersLockedInSomeMethods(file_path : str):
    eventSrc = EventSource()
    locked_in_some_observer = lockedInSomeObserver()
    eventSrc.addObserver(locked_in_some_observer)
    searchNodes(file_path, eventSrc)
    if locked_in_some_observer.errors:
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
    This won't get the data members inside of the methods, just the data members of the class itself.
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


# TODO: Add handling for parameters (Can give false positives otherwise)
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
    lockguard_scope_pairs = []
    lock_unlock_pairs = []
    lock_member_pairs = []
    unlock_member_pairs = []
    method_variables = []
    compound_statements = []
    nextMemberIsInLock = False
    nextMemberIsInUnlock = False
    for child in methodCursor.walk_preorder():
        if (child.kind == clang.cindex.CursorKind.CALL_EXPR):
            if (child.type.spelling == "std::lock_guard<std::mutex>" and child.displayname == "lock_guard"):
                scope_pair = getScopePair(child, reversed(compound_statements))
                if scope_pair:
                    lockguard_scope_pairs.append(scope_pair)
            elif(child.displayname == "lock"):
                currentLock = child
                nextMemberIsInLock = True
            elif (child.displayname == "unlock"):
                currentUnlock = child
                nextMemberIsInUnlock = True
        elif child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            compound_statements.append(child)
        elif child.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR or child.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR:
            for variable in class_variables:
                # I have the namespace_ref check here so that if the variable has a name like 'std' it won't confuse it with the std namespace reference
                # Although it is bad coding practice to name things after what's in the namespace, this will still perform as it should if variables are named in such a way
                # The type and kind of our variables isn't rigid, which is why I'm not comparing them
                if (child.spelling == variable.spelling) and (child.kind != clang.cindex.CursorKind.NAMESPACE_REF):
                    method_variables.append(child)
            if child.type.spelling == 'std::_Mutex_base':
                if nextMemberIsInLock and child.extent.start.line == currentLock.extent.start.line:
                    lock_member_pairs.append( (currentLock, child) )
                    nextMemberIsInLock = False
                elif nextMemberIsInUnlock and child.extent.start.line == currentUnlock.extent.start.line:
                    unlock_member_pairs.append( (currentUnlock, child) )
                    nextMemberIsInUnlock = False
    if (unlock_member_pairs):
        lock_unlock_pairs = getLockUnlockPairs(lock_member_pairs, unlock_member_pairs, method_variables)
    return lockguard_scope_pairs, method_variables, lock_unlock_pairs

def getLockUnlockPairs(lock_member_pairs : list, unlock_member_pairs : list, method_variables : list):
    lock_unlock_member_pairs = [] # [ (lock_node, member_node.spelling, unlock_node) ]
    for lock_pair in lock_member_pairs:
        for unlock_pair in unlock_member_pairs:
            if lock_pair[1].spelling == unlock_pair[1].spelling:
                lock_unlock_member_pairs.append( (lock_pair[0], lock_pair[1].spelling, unlock_pair[0]) )
                unlock_member_pairs.remove(unlock_pair)
                break
    return lock_unlock_member_pairs
            

        

def getScopePair(Cursor : clang.cindex.Cursor, compound_statements : list):
    """Given a Cursor and a list of scopes (compound statements), this will return
    a tuple of the (Cursor, scope) pairing.
    If the scope isn't found in the list, it will return None
    It would be wise to reverse() the list, as AST's typically find nested scopes last,

    Args:
        Cursor (clang.cindex.Cursor) : The cursor to find the scope of
        compound_statements(list): A list of cursors of kind 'clang.cindex.CursorKind.COMPOUND_STMT' to check if the cursor is inside of
    Returns:
        tuple((clang.cindex.Cursor, clang.cindex.Cursor)): If the scope was found, return (Cursor, scope)
        None: If scope was not found
    """
    for compound_statement in compound_statements:
        if compound_statement.extent.start.line <= Cursor.extent.start.line and compound_statement.extent.end.line >= Cursor.extent.end.line:
            return (Cursor, compound_statement)
    return None