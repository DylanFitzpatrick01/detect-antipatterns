# Gráinne Ready
# SIDENOTE: Call the 'def checkIfMembersLockedInSomeMethods(file_path : str):' function to check for the anti-pattern
from alerts import *
from typing import List
from formalCheckInterface import FormalCheckInterface
from Util import *
import clang.cindex

class Check(FormalCheckInterface):
	unlockedVar = list()
	lockedVar = list()

	def __init__(self):   
		self.inside = None  			#Check if we're in cxx method (class method)

		self.lock_guards = list()	
		self.locks = list()
		self.scopeLevel = 0

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if self.inside != clang.cindex.CursorKind.CXX_METHOD:
			return
		
		if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			if cursor.spelling == "lock":
				self.locks.append(Lock(cursor))
			elif cursor.spelling == "unlock":
				for lock in self.locks:
					# If the referenced mutex of the unlock matches the lock, remove the lock
					if lock.mutex == list(list(cursor.get_children())[0].get_children())[0].referenced.get_usr():
						self.locks.remove(lock)
			elif cursor.spelling == "lock_guard":
				self.lock_guards.append(Lock_Guard(cursor, self.scopeLevel))
		elif cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR and cursor.type.spelling != "std::mutex":
			newVar = Var(cursor)
			print(cursor.type.spelling)
			print(newVar.usr)
			print(newVar.line)
			if self.locks or self.lock_guards:

				#Only need one example of it being locked to flag the error
				if newVar not in Check.lockedVar:
					print("locked")
					Check.lockedVar.append(newVar)

				if newVar in Check.unlockedVar:
					print("Already unlocked\n")

					newAlert = Alert(cursor.translation_unit, cursor.extent, 
						f"Data member '{cursor.displayname}' at (line: {cursor.extent.start.line}, column: {cursor.extent.start.column}) is accessed with a lock_guard or lock/unlock combination in this method, "+
						f"\nbut is not accessed with a lock_guard or lock/unlock combination in other methods\n "+
						f"Are you missing a lock_guard or lock/unlock combination in other methods which use '{cursor.displayname}'?", "error")
 
					if newAlert not in alerts:
						alerts.append(newAlert)
			else:
				#Only need one example of it being unlocked to flag the error
				if newVar not in Check.unlockedVar:
					print("unlocked")
					Check.unlockedVar.append(newVar)

				if newVar in Check.lockedVar:
					print("Already locked\n")

					newAlert = Alert(cursor.translation_unit, cursor.extent, 
						f"Data member '{cursor.displayname}' at (line: {cursor.extent.start.line}, column: {cursor.extent.start.column}) is not accessed with a lock_guard or lock/unlock combination in this method, "+
						f"\nbut is accessed with a lock_guard or lock/unlock combination in other methods\n "+
						f"Are you missing a lock_guard or lock/unlock combination before '{cursor.displayname}'?", "error")
 
					if newAlert not in alerts:
						alerts.append(newAlert)
					

	def __eq__(self, __o: object) -> bool:
		if type(self) != type(__o):
			return False

		#The numbers can only change if new lock guard made
		if len(self.lock_guards) != len(__o.lock_guards):
			return False
		
		for i in range(0, len(self.lock_guards)):
			if self.lock_guards[i] != __o.lock_guards[i]:
				return False

		if len(self.locks) != len(__o.locks):
			return False
		
		for i in range(0, len(self.locks)):
			if self.locks[i] != __o.locks[i]:
				return False
			
		return True

	def copy(self):
		copy = Check()

		for lockGuard in self.lock_guards:
			copy.lock_guards.append(lockGuard.copy())

		for lock in self.locks:
			copy.locks.append(lock.copy())

		copy.scopeLevel = self.scopeLevel
		copy.inside = self.inside

		return copy
	
	def scope_increased(self, alerts):
		self.scopeLevel += 1

	# Removes all Lock_Guards that have exited the scope
	def scope_decreased(self, alerts):
		self.scopeLevel -= 1

		for lockGuard in self.lock_guards:
			if lockGuard.scopeLevel >= self.scopeLevel:
				self.lock_guards.remove(lockGuard)

	# Resets all state to default
	def new_function(self, cursor, alerts):
		self.inside = cursor.kind

		self.lock_guards = list()
		self.locks = list()
		self.scopeLevel = 0


# class Check(FormalCheckInterface):
# 	"""
# 	NOTE: This expects the nodes being fed into it to be in a PREORDER traversal
# 	"""

# 	def __init__(self):
# 		"""
# 		Initialiser, Creates an instance of the lockedInSomeObserver class

# 		Args:
# 			None

# 		Returns:
# 			None
# 		"""
# 		self.classFound = False
# 		self.cursor_is_in_method = False
# 		self.currentClass = None
# 		self.currentMethod = None
# 		self.data_members = []
# 		self.method_data_members = []
# 		self.lockguard_scope_pairs = []
# 		self.lock_unlock_pairs = []
# 		self.lock_member_pairs = []
# 		self.unlock_member_pairs = []
# 		self.method_variables = []
# 		self.compound_statements = []
# 		self.variables_under_lock = {}
# 		self.nextMemberIsInLock = False
# 		self.nextMemberIsInUnlock = False


# 	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts: List[Alert]):
# 		"""Updates the lockedInSomeObserver with the current Node in the AST

# 		Args:
# 			cursor (clang.cindex.Cursor): A node from the AST
		
# 		Returns:
# 			None
		
# 		Detailed Description:
# 			Checks if the cursor is the declaration of a class
# 			If it is, it will get all data members of the class.
			
# 			If the cursor is a method inside the class, it will
# 			take note of this and store information about lock_guards, locks, unlocks, compound statements and class data members being used in the method
			
# 			If the previous node was inside a method, and the cursor is not inside that method, then the method has ended, and we will check
# 			if any of the data members of the class were guarded or not in the method and compare this state to if they were guarded or not in a previous method.
# 			If either a data member was guarded in this method but not in another, or a data member was not guarded in this method but guarded in another, it will raise an error (and store it).
# 			After an error was raised or not, it will clear information of that method from the observer to make way for any future methods.
			
# 			If the previous node was inside a class, and the cursor is not inside that class, then the class has ended, and we will clear
# 			all information about that class from the observer except the errors that class had, so it can make way for any future classes in the file.
# 		"""
# 		# If the current node is the declaration of a class
# 		if cursor.kind == clang.cindex.CursorKind.CLASS_DECL:
# 			self.classFound = True
# 			self.currentClass = cursor
# 			# Get the data members of the class
# 			self.data_members = getDataMembersInClass(cursor)

# 		if (self.classFound):
# 			# If the cursor's line is less than or equal to the end of the class scope's line
# 			if (cursor.extent.start.line <= self.currentClass.extent.end.line):
# 				# If the previous nodes were in a method
# 				if (self.cursor_is_in_method):
# 					# If this node is still in the method
# 					if (cursor.extent.start.line <= self.currentMethod.extent.end.line):
# 						# Check if the cursor is a call expression (if it is, it could be a lock_guard, lock, or unlock)
# 						if (not self.checkIfCallExpr(cursor)):
# 							# If the node isn't a call expression, check if it is a compound statement aka '{}'
# 							if cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT:
# 								self.compound_statements.append(cursor)
# 							# If the node isn't a compound statement, check if it is a data member
# 							else:
# 								self.checkIfDataMemberOfClass(cursor)
# 								# If it isn't a data member, we don't need it, so wait until the next cursor is fed into update()

# 					# Else, if this node is the not in the method (but the previous nodes were)
# 					else:
# 						# Check for the antipattern and then clear the method information from the observer
# 						self.checkForAntipattern(alerts)
# 						# Check if the cursor is a different method
# 						if cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
# 							self.cursor_is_in_method = True
# 							self.currentMethod = cursor
# 						else:
# 							self.cursor_is_in_method = False

# 				# Otherwise check if the cursor is a method
# 				elif cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
# 					self.cursor_is_in_method = True
# 					self.currentMethod = cursor
# 			# Else, we ran through all the nodes in that class, and the current node is not in the class
# 			# Clear the observer
# 			else:
# 				self.clearObserverAfterClass()
# 				if cursor.kind != clang.cindex.CursorKind.CLASS_DECL:
# 					self.classFound = False


# 	def checkIfDataMemberOfClass(self, cursor):
# 		"""Checks if the cursor is a data member of the class

# 		Args:
# 			cursor (clang.cindex.Cursor): The cursor to check

# 		Returns:
# 			bool: True if it is a data member of the class
# 				  False if it is not a data member of the class
# 		"""
# 		if cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR or cursor.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR or cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
# 			if (cursor.type.spelling == "std::_Mutex_base"):
# 				# If the next member we're looking for is in a lock (e.g. mDataAccess in mDataAccess.lock())
# 				if self.nextMemberIsInLock and cursor.extent.start.line == self.currentLock.extent.start.line:
# 					# Add the (lock cursor, member cursor) tuple to the lock_member_pairs list
# 					self.lock_member_pairs.append( (self.currentLock, cursor) )
# 					self.nextMemberIsInLock = False
# 				# Else If the next member we're looking for is in a unlock (e.g. mDataAccess in mDataAccess.unlock())
# 				elif self.nextMemberIsInUnlock and cursor.extent.start.line == self.currentUnlock.extent.start.line:
# 					# Add the (unlock cursor, member cursor) tuple to the unlock_member_pairs list
# 					self.unlock_member_pairs.append( (self.currentUnlock, cursor) )
# 					self.nextMemberIsInUnlock = False
# 		# Check if cursor is a data member of the class itself
# 		for variable in self.data_members:
# 			if (cursor.spelling == variable.spelling):
# 				# If it is, add it to the method_variables list
# 				self.method_variables.append(cursor)
# 				return True
# 		return False


# 	def checkIfCallExpr(self, cursor : clang.cindex.Cursor):
# 		"""Checks if the cursor is a call expression. If so, it will check if it is a lock_guard, lock, or unlock and
# 		add it to the respective list if is.

# 		Args:
# 			cursor (clang.cindex.Cursor): The cursor to check

# 		Returns:
# 			bool: True if it is a call expression
# 				  False if it is not a call expression
# 		"""
# 		if not (self.nextMemberIsInLock or self.nextMemberIsInUnlock):
# 			if (cursor.kind == clang.cindex.CursorKind.CALL_EXPR):
# 				# if the cursor is a lock_guard
# 				if (cursor.type.spelling == "std::lock_guard<std::mutex>" and cursor.displayname == "lock_guard"):
# 					# get the compound_statement the lock_guard is inside and combine the lock_guard and compound_statement
# 					# into a tuple (lock_guard_cursor, compound_statement_cursor)
# 					scope_pair = self.getScopePair(cursor, reversed(self.compound_statements))
# 					if scope_pair:
# 						self.lockguard_scope_pairs.append(scope_pair)
# 					return True
# 				# Otherwise, if the cursor is a lock
# 				elif(cursor.displayname == "lock"):
# 					# Store it as the current lock, we know that the next data member we come across will be the mutex being locked, so set
# 					# the bool which determines this to true for when we run into it in checkIfDataMemberOfClass()
# 					self.currentLock = cursor
# 					self.nextMemberIsInLock = True
# 					return True
# 				# Otherwise, if the cursor is an unlock
# 				elif (cursor.displayname == "unlock"):
# 					# Store it as the current unlock, we know that the next data member we come across will be the mutex being unlocked, so set
# 					# the bool which determines this to true for when we run into it in checkIfDataMemberOfClass()
# 					self.currentUnlock = cursor
# 					self.nextMemberIsInUnlock = True
# 					return True
# 		return False


# 	#Now uses method call from main
# 	def new_function(self, alerts):
# 		"""Clears all the information about a method from the observer
# 		To be used once all the cursors in a method were ran through, and the current cursor (if there still is one) is the first cursor outside of the method
# 		"""
# 		self.currentMethod = None
# 		self.cursor_is_in_method = False
# 		self.method_data_members = []
# 		self.lockguard_scope_pairs = []
# 		self.lock_unlock_pairs = []
# 		self.method_variables = []
# 		self.nextMemberIsInLock = False
# 		self.nextMemberIsInUnlock = False


# 	def clearObserverAfterClass(self):
# 		"""Clears all the information about a class from the observer
# 		To be used once all the cursors in a class were ran through, and the current cursor (if there still is one) is the first cursor outside of the class
# 		"""
# 		self.cursor_is_in_method = False
# 		self.currentClass = None
# 		self.methods = []
# 		self.data_members = []
# 		self.lockguard_scope_pairs = []
# 		self.lock_unlock_pairs = []
# 		self.method_variables = []
# 		self.compound_statements = []
# 		self.variables_under_lock = {}
# 		self.nextMemberIsInLock = False
# 		self.nextMemberIsInUnlock = False


# 	def checkForAntipattern(self, alerts: List[Alert]):
# 		"""
# 		Checks if any of the data members of the class were guarded or not in the method and compare this state to if they were guarded or not in a previous method.
# 		If either a data member was guarded in this method but not in another, or a data member was not guarded in this method but guarded in another, it will raise an error (and store it).
# 		"""
# 		# If there are unlocks in the method, get the lock/unlock pairs. These are tuples ( lock_cursor, name_of_member_being_locked, unlock_cursor )
# 		if (self.unlock_member_pairs):
# 			self.lock_unlock_pairs = self.getLockUnlockPairs(self.lock_member_pairs, self.unlock_member_pairs)
# 			self.lock_member_pairs = []
# 			self.unlock_member_pairs = []
# 		for method_variable in self.method_variables:
# 			# If the data member is within the guarded scope of a lock_guard, log in the dictionary that it is locked in the method
# 			if any(lock[0].extent.start.line <= method_variable.extent.start.line and lock[1].extent.end.line >= method_variable.extent.end.line for lock in self.lockguard_scope_pairs):
# 				# If the data member was not guarded in a previous method, raise an error
# 				if method_variable.displayname in self.variables_under_lock and not self.variables_under_lock[method_variable.displayname]:
# 					self.raiseError(self.currentMethod, method_variable, True, alerts)
# 				self.variables_under_lock[method_variable.displayname] = True
# 			# Otherwise, If the data member is within the guarded scope of a lock/unlock combiantion, log in the dictionary that it is locked in the method
# 			elif any(lock_unlock_pair[0].extent.start.line <= method_variable.extent.start.line and lock_unlock_pair[2].extent.end.line >= method_variable.extent.end.line for lock_unlock_pair in self.lock_unlock_pairs):
# 				# If the data member was not guarded in a previous method, raise an error
# 				if method_variable.displayname in self.variables_under_lock and not self.variables_under_lock[method_variable.displayname]:
# 					self.raiseError(self.currentMethod, method_variable, True, alerts)
# 				self.variables_under_lock[method_variable.displayname] = True
# 			# Otherwise, it is not guarded, so log in the dictionary that it isn't locked
# 			else:
# 				# If the data member was guarded in a previous method, raise an error
# 				if method_variable.displayname in self.variables_under_lock and self.variables_under_lock[method_variable.displayname]:
# 					self.raiseError(self.currentMethod, method_variable, False, alerts)
# 				self.variables_under_lock[method_variable.displayname] = False


# 	def raiseError(self, methodNode : clang.cindex.Cursor, memberNode : clang.cindex.Cursor, isLockedInMethod : bool, alerts: List[Alert]):
# 		"""
# 		Raises an error, indicating that a data member is locked in some, but not all methods
		
# 		Args:
# 			methodNode (clang.cindex.Cursor): The node which represents the declaration of the method that the error-causing data member is inside of
# 			memberNode (clang.cindex.Cursor): The node which represents the data member inside the method which is locked in some, but not all methods
# 			isLockedInMethod (bool): A boolean which indicates whether the member was under lock or not in the specific method (This adjusts the error message)
		
# 		Returns:
# 			None
# 		"""
# 		if (isLockedInMethod):
# 			alerts.append(Alert(memberNode.translation_unit, methodNode.extent, 
# 				f"Data member '{memberNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is accessed with a lock_guard or lock/unlock combination in this method, "+
# 				f"\nbut is not accessed with a lock_guard or lock/unlock combination in other methods\n "+
# 				f"Are you missing a lock_guard or lock/unlock combination in other methods which use '{memberNode.displayname}'?", "error"))
 
# 		else:
# 			alerts.append(Alert(memberNode.translation_unit, methodNode.extent, 
# 				f"Data member '{memberNode.displayname}' at (line: {memberNode.extent.start.line}, column: {memberNode.extent.start.column}) is not accessed with a lock_guard or lock/unlock combination in this method, "+
# 				f"\nbut is accessed with a lock_guard or lock/unlock combination in other methods\n "+
# 				f"Are you missing a lock_guard before '{memberNode.displayname}'?", "error"))

# 	def getLockUnlockPairs(self, lock_member_pairs : list, unlock_member_pairs : list):
# 		"""
# 		Compares a list of tuples that are lock cursors paired with their respective member cursors, and unlock cursors paired with their respective member
# 		cursors, and matches the lock cursor to its unlock. When they are matched, it will add a tuple (lock_cursor, member_being_locked_cursor, unlock_cursor) to
# 		a list and return a list of such tuples at the end.

# 		Args:
# 			lock_member_pairs (list): A list of tuples where each element is a clang.cindex.Cursor (lock_cursor, member_being_locked_cursor)
# 			unlock_member_pairs (list): A list of tuples where each element is a clang.cindex.Cursor (unlock_cursor, member_being_unlocked_cursor)

# 		Returns:
# 			list: A list of tuples that pair the lock cursor, member name that's being locked, and the unlock cursor together 
# 					Tuple format: ( lock_cursor(clang.cindex.Cursor), name of member being locked(str), unlock_cursor(clang.cindex.Cursor) ) 
# 		"""
# 		lock_unlock_member_pairs = []
# 		unlock_prs = unlock_member_pairs.copy()
# 		for lock_pair in lock_member_pairs:
# 			for unlock_pair in unlock_prs:
# 				# If the spelling of the member being locked in the lock_cursor is the same as the unlock_cursor
# 				if lock_pair[1].spelling == unlock_pair[1].spelling:
# 					# Add the matching lock/member/unlock tuple to the return list
# 					lock_unlock_member_pairs.append( (lock_pair[0], lock_pair[1].spelling, unlock_pair[0]) )
# 					unlock_prs.remove(unlock_pair)
# 					break
# 		return lock_unlock_member_pairs


# 	def getScopePair(self, Cursor : clang.cindex.Cursor, compound_statements : list):
# 		"""Given a Cursor and a list of scopes (compound statements), this will return
# 		a tuple of the respective (Cursor, scope) pairing.
# 		If the scope isn't found in the list, it will return None
# 		It would be wise to reverse() the list when calling this function, as AST's typically find nested scopes last

# 		Args:
# 			Cursor (clang.cindex.Cursor) : The cursor to find the scope of
# 			compound_statements(list): A list of cursors of kind 'clang.cindex.CursorKind.COMPOUND_STMT' to check if the cursor is inside of
# 		Returns:
# 			tuple((clang.cindex.Cursor, clang.cindex.Cursor)): If the scope was found, return (Cursor, scope)
# 			None: If scope was not found
# 		"""
# 		for compound_statement in compound_statements:
# 			if compound_statement.extent.start.line <= Cursor.extent.start.line and compound_statement.extent.end.line >= Cursor.extent.end.line:
# 				return (Cursor, compound_statement)
# 		return None


# # Gráinne Ready
# def getDataMembersInClass(classCursor : clang.cindex.Cursor):
# 	"""Gets all the cursors which are data members that are the children of a class and returns them in a list
# 	This won't get the data members inside of the methods, just the data members of the class itself.
# 	Args:
# 		classCursor (clang.cindex.Cursor): A cursor of kind 'clang.cindex.CursorKind.CLASS_DECL'
	
# 	Returns:
# 		data_members (list of clang.cindex.Cursor): A list of cursors which represent the data members of the class (class variables)
# 	"""
# 	data_members = []
# 	for child in classCursor.get_children():
# 		# If the child is a field declaration, we know it's a data member
# 		if child.kind == clang.cindex.CursorKind.FIELD_DECL:
# 			data_members.append(child)
# 	return data_members