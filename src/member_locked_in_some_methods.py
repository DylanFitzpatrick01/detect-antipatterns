# Gráinne Ready
# SIDENOTE: Call the 'def checkIfMembersLockedInSomeMethods(file_path : str):' function to check for the anti-pattern
from output import *
from observer import *
import clang.cindex


class lockedInSomeObserver(Observer):
    """
    NOTE: This expects the nodes being fed into it to be in a PREORDER traversal
    """

    def __init__(self):
        """
        Initialiser, Creates an instance of the lockedInSomeObserver class

        Args:
            None

        Returns:
            None
        """
        self.errors = ""
        self.classFound = False
        self.currentNode_is_in_method = False
        self.currentClass = None
        self.currentMethod = None
        self.data_members = []
        self.method_data_members = []
        self.lockguard_scope_pairs = []
        self.lock_unlock_pairs = []
        self.lock_member_pairs = []
        self.unlock_member_pairs = []
        self.method_variables = []
        self.compound_statements = []
        self.variables_under_lock = {}
        self.nextMemberIsInLock = False
        self.nextMemberIsInUnlock = False


    def update(self, currentNode : clang.cindex.Cursor):
        """Updates the lockedInSomeObserver with the current Node in the AST

        Args:
            currentNode (clang.cindex.Cursor): A node from the AST
        
        Returns:
            None
        
        Detailed Description:
            Checks if the currentNode is the declaration of a class
            If it is, it will get all data members of the class.
            
            If the currentNode is a method inside the class, it will
            take note of this and store information about lock_guards, locks, unlocks, compound statements and class data members being used in the method
            
            If the previous node was inside a method, and the currentNode is not inside that method, then the method has ended, and we will check
            if any of the data members of the class were guarded or not in the method and compare this state to if they were guarded or not in a previous method.
            If either a data member was guarded in this method but not in another, or a data member was not guarded in this method but guarded in another, it will raise an error (and store it).
            After an error was raised or not, it will clear information of that method from the observer to make way for any future methods.
            
            If the previous node was inside a class, and the currentNode is not inside that class, then the class has ended, and we will clear
            all information about that class from the observer except the errors that class had, so it can make way for any future classes in the file.
        """
        # If the current node is the declaration of a class
        if currentNode.kind == clang.cindex.CursorKind.CLASS_DECL:
            self.classFound = True
            self.currentClass = currentNode
            # Get the data members of the class
            self.data_members = getDataMembersInClass(currentNode)

        if (self.classFound):
            # If the currentNode's line is less than or equal to the end of the class scope's line
            if (currentNode.extent.start.line <= self.currentClass.extent.end.line):
                # If the previous nodes were in a method
                if (self.currentNode_is_in_method):
                    # If this node is still in the method
                    if (currentNode.extent.start.line <= self.currentMethod.extent.end.line):
                        # Check if the currentNode is a call expression (if it is, it could be a lock_guard, lock, or unlock)
                        if (not self.checkIfCallExpr(currentNode)):
                            # If the node isn't a call expression, check if it is a compound statement aka '{}'
                            if currentNode.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                                self.compound_statements.append(currentNode)
                            # If the node isn't a compound statement, check if it is a data member
                            else:
                                self.checkIfDataMemberOfClass(currentNode)
                                # If it isn't a data member, we don't need it, so wait until the next cursor is fed into update()

                    # Else, if this node is the not in the method (but the previous nodes were)
                    else:
                        # Check for the antipattern and then clear the method information from the observer
                        self.checkForAntipattern()
                        self.clearObserverAfterMethod()
                        # Check if the currentNode is a different method
                        if currentNode.kind == clang.cindex.CursorKind.CXX_METHOD:
                            self.currentNode_is_in_method = True
                            self.currentMethod = currentNode
                        else:
                            self.currentNode_is_in_method = False

                # Otherwise check if the currentNode is a method
                elif currentNode.kind == clang.cindex.CursorKind.CXX_METHOD:
                    self.currentNode_is_in_method = True
                    self.currentMethod = currentNode
            # Else, we ran through all the nodes in that class, and the current node is not in the class
            # Clear the observer
            else:
                self.clearObserverAfterClass()
                if currentNode.kind != clang.cindex.CursorKind.CLASS_DECL:
                    self.classFound = False


    def checkIfDataMemberOfClass(self, currentNode):
        """Checks if the currentNode is a data member of the class

        Args:
            currentNode (clang.cindex.Cursor): The cursor to check

        Returns:
            bool: True if it is a data member of the class
                  False if it is not a data member of the class
        """
        if not (self.nextMemberIsInLock or self.nextMemberIsInUnlock):
            if currentNode.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR or currentNode.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR or currentNode.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                # If the next member we're looking for is in a lock (e.g. mDataAccess in mDataAccess.lock())
                if self.nextMemberIsInLock and currentNode.extent.start.line == self.currentLock.extent.start.line:
                    # Add the (lock cursor, member cursor) tuple to the lock_member_pairs list
                    self.lock_member_pairs.append( (self.currentLock, currentNode) )
                    self.nextMemberIsInLock = False
                # Else If the next member we're looking for is in a unlock (e.g. mDataAccess in mDataAccess.unlock())
                elif self.nextMemberIsInUnlock and currentNode.extent.start.line == self.currentUnlock.extent.start.line:
                    # Add the (unlock cursor, member cursor) tuple to the unlock_member_pairs list
                    self.unlock_member_pairs.append( (self.currentUnlock, currentNode) )
                    self.nextMemberIsInUnlock = False
                # Check if currentNode is a data member of the class itself
                for variable in self.data_members:
                    if (currentNode.spelling == variable.spelling):
                        # If it is, add it to the method_variables list
                        self.method_variables.append(currentNode)
                        return True
        return False


    def checkIfCallExpr(self, currentNode : clang.cindex.Cursor):
        """Checks if the currentNode is a call expression. If so, it will check if it is a lock_guard, lock, or unlock and
        add it to the respective list if is.

        Args:
            currentNode (clang.cindex.Cursor): The cursor to check

        Returns:
            bool: True if it is a call expression
                  False if it is not a call expression
        """
        if not (self.nextMemberIsInLock or self.nextMemberIsInUnlock):
            if (currentNode.kind == clang.cindex.CursorKind.CALL_EXPR):
                # if the currentNode is a lock_guard
                if (currentNode.type.spelling == "std::lock_guard<std::mutex>" and currentNode.displayname == "lock_guard"):
                    # get the compound_statement the lock_guard is inside and combine the lock_guard and compound_statement
                    # into a tuple (lock_guard_cursor, compound_statement_cursor)
                    scope_pair = getScopePair(currentNode, reversed(self.compound_statements))
                    if scope_pair:
                        self.lockguard_scope_pairs.append(scope_pair)
                    return True
                # Otherwise, if the currentNode is a lock
                elif(currentNode.displayname == "lock"):
                    # Store it as the current lock, we know that the next data member we come across will be the mutex being locked, so set
                    # the bool which determines this to true for when we run into it in checkIfDataMemberOfClass()
                    self.currentLock = currentNode
                    self.nextMemberIsInLock = True
                    return True
                # Otherwise, if the currentNode is an unlock
                elif (currentNode.displayname == "unlock"):
                    # Store it as the current unlock, we know that the next data member we come across will be the mutex being unlocked, so set
                    # the bool which determines this to true for when we run into it in checkIfDataMemberOfClass()
                    self.currentUnlock = currentNode
                    self.nextMemberIsInUnlock = True
                    return True
        return False


    def clearObserverAfterMethod(self):
        """Clears all the information about a method from the observer
        To be used once all the cursors in a method were ran through, and the current cursor (if there still is one) is the first cursor outside of the method
        """
        self.currentMethod = None
        self.method_data_members = []
        self.lockguard_scope_pairs = []
        self.lock_unlock_pairs = []
        self.method_variables = []
        self.nextMemberIsInLock = False
        self.nextMemberIsInUnlock = False


    def clearObserverAfterClass(self):
        """Clears all the information about a class from the observer
        To be used once all the cursors in a class were ran through, and the current cursor (if there still is one) is the first cursor outside of the class
        """
        self.currentNode_is_in_method = False
        self.currentClass = None
        self.methods = []
        self.data_members = []
        self.lockguard_scope_pairs = []
        self.lock_unlock_pairs = []
        self.method_variables = []
        self.compound_statements = []
        self.variables_under_lock = {}
        self.nextMemberIsInLock = False
        self.nextMemberIsInUnlock = False


    def checkForAntipattern(self):
        """
        Checks if any of the data members of the class were guarded or not in the method and compare this state to if they were guarded or not in a previous method.
        If either a data member was guarded in this method but not in another, or a data member was not guarded in this method but guarded in another, it will raise an error (and store it).
        """
        # If there are unlocks in the method, get the lock/unlock pairs. These are tuples ( lock_cursor, name_of_member_being_locked, unlock_cursor )
        if (self.unlock_member_pairs):
            self.lock_unlock_pairs = getLockUnlockPairs(self.lock_member_pairs, self.unlock_member_pairs)
            self.lock_member_pairs = []
            self.unlock_member_pairs = []
        for method_variable in self.method_variables:
            # If the data member is within the guarded scope of a lock_guard, log in the dictionary that it is locked in the method
            if any(lock[0].extent.start.line <= method_variable.extent.start.line and lock[1].extent.end.line >= method_variable.extent.end.line for lock in self.lockguard_scope_pairs):
                # If the data member was not guarded in a previous method, raise an error
                if method_variable.displayname in self.variables_under_lock and not self.variables_under_lock[method_variable.displayname]:
                    self.raiseError(self.currentMethod, method_variable, isLockedInMethod=True)
                self.variables_under_lock[method_variable.displayname] = True
            # Otherwise, If the data member is within the guarded scope of a lock/unlock combiantion, log in the dictionary that it is locked in the method
            elif any(lock_unlock_pair[0].extent.start.line <= method_variable.extent.start.line and lock_unlock_pair[2].extent.end.line >= method_variable.extent.end.line for lock_unlock_pair in self.lock_unlock_pairs):
                # If the data member was not guarded in a previous method, raise an error
                if method_variable.displayname in self.variables_under_lock and not self.variables_under_lock[method_variable.displayname]:
                    self.raiseError(self.currentMethod, method_variable, isLockedInMethod=True)
                self.variables_under_lock[method_variable.displayname] = True
            # Otherwise, it is not guarded, so log in the dictionary that it isn't locked
            else:
                # If the data member was guarded in a previous method, raise an error
                if method_variable.displayname in self.variables_under_lock and self.variables_under_lock[method_variable.displayname]:
                    self.raiseError(self.currentMethod, method_variable, isLockedInMethod=False)
                self.variables_under_lock[method_variable.displayname] = False


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
                f"Data member '{memberNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is accessed with a lock_guard or lock/unlock combination in this method, "+
                f"\nbut is not accessed with a lock_guard or lock/unlock combination in other methods\n "+
                f"Are you missing a lock_guard or lock/unlock combination in other methods which use '{memberNode.displayname}'?", "error")
            self.errors += f"""Data member '{methodNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is accessed with a lock_guard or lock/unlock combination in this method,
but is not accessed with a lock_guard or lock/unlock combination in other methods
 Are you missing a lock_guard or lock/unlock combination in other methods which use '{methodNode.displayname}'?"""
 
        else:
            print_error(memberNode.translation_unit, methodNode.extent, 
                f"Data member '{memberNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is not accessed with a lock_guard or lock/unlock combination in this method, "+
                f"\nbut is accessed with a lock_guard or lock/unlock combination in other methods\n "+
                f"Are you missing a lock_guard before '{memberNode.displayname}'?", "error")
            self.errors += f"""Data member '{memberNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is not accessed with a lock_guard or lock/unlock combination in this method,
but is accessed with a lock_guard or lock/unlock combination in other methods
 Are you missing a lock_guard before '{memberNode.displayname}'?"""


# MAIN FUNCTION FOR THIS ANTI-PATTERN AT THE MOMENT
# Gráinne Ready
def checkIfMembersLockedInSomeMethods(file_path : str):
    """
    Checks for 'data members locked in some, but not all methods' antipattern
    
    Args:
        file_path (str): The path of the c++ file to check for the antipattern
    
    Returns:
        errors (str): Information about the errors found, if there were instances of the antipattern detected in the file
        "PASSED - For data members locked in some, but not all methods" (str): If there were no errors detected
    """
    eventSrc = EventSource()
    locked_in_some_observer = lockedInSomeObserver()
    eventSrc.addObserver(locked_in_some_observer)
    searchNodes(file_path, eventSrc)
    # If the observer's errors string is not empty, there were errors so return it. Otherwise, no errors were found so return that the file passed
    if locked_in_some_observer.errors:
        return locked_in_some_observer.errors
    print("PASSED - For data members locked in some, but not all methods")
    return "PASSED - For data members locked in some, but not all methods"


# Gráinne Ready
def searchNodes(file_path : str, eventSrc: EventSource):
    """
    Searches through every node in a c++ file (AST) and notifies Observers in the EventSource about it
    
    Args:
        file_path (str): The path of the c++ file to check for the antipattern
        eventSrc (EventSource): The EventSource object to notify observer with
    
    Returns:
        None
    """
    index = clang.cindex.Index.create()
    tu = index.parse(file_path)
    for cursor in tu.cursor.walk_preorder():
        # This if statement makes sure only nodes that are inside the file itself are fed into the Observers
        if(str(cursor.translation_unit.spelling) == str(cursor.location.file)):
            eventSrc.notifyObservers(cursor)


# Gráinne Ready
def getDataMembersInClass(classCursor : clang.cindex.Cursor):
    """Gets all the cursors which are data members that are the children of a class and returns them in a list
    This won't get the data members inside of the methods, just the data members of the class itself.
    Args:
        classCursor (clang.cindex.Cursor): A cursor of kind 'clang.cindex.CursorKind.CLASS_DECL'
    
    Returns:
        data_members (list of clang.cindex.Cursor): A list of cursors which represent the data members of the class (class variables)
    """
    data_members = []
    for child in classCursor.get_children():
        # If the child is a field declaration, we know it's a data member
        if child.kind == clang.cindex.CursorKind.FIELD_DECL:
            data_members.append(child)
    return data_members


def getLockUnlockPairs(lock_member_pairs : list, unlock_member_pairs : list):
    """
    Compares a list of tuples that are lock cursors paired with their respective member cursors, and unlock cursors paired with their respective member
    cursors, and matches the lock cursor to its unlock. When they are matched, it will add a tuple (lock_cursor, member_being_locked_cursor, unlock_cursor) to
    a list and return a list of such tuples at the end.
    
    Args:
        lock_member_pairs (list): A list of tuples where each element is a clang.cindex.Cursor (lock_cursor, member_being_locked_cursor)
        unlock_member_pairs (list): A list of tuples where each element is a clang.cindex.Cursor (unlock_cursor, member_being_unlocked_cursor)

    Returns:
        list: A list of tuples that pair the lock cursor, member name that's being locked, and the unlock cursor together 
                Tuple format: ( lock_cursor(clang.cindex.Cursor), name of member being locked(str), unlock_cursor(clang.cindex.Cursor) ) 
    """
    lock_unlock_member_pairs = []
    unlock_prs = unlock_member_pairs.copy()
    for lock_pair in lock_member_pairs:
        for unlock_pair in unlock_prs:
            # If the spelling of the member being locked in the lock_cursor is the same as the unlock_cursor
            if lock_pair[1].spelling == unlock_pair[1].spelling:
                # Add the matching lock/member/unlock tuple to the return list
                lock_unlock_member_pairs.append( (lock_pair[0], lock_pair[1].spelling, unlock_pair[0]) )
                unlock_prs.remove(unlock_pair)
                break
    return lock_unlock_member_pairs
            

def getScopePair(Cursor : clang.cindex.Cursor, compound_statements : list):
    """Given a Cursor and a list of scopes (compound statements), this will return
    a tuple of the respective (Cursor, scope) pairing.
    If the scope isn't found in the list, it will return None
    It would be wise to reverse() the list when calling this function, as AST's typically find nested scopes last

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