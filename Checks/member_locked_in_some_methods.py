# Gráinne Ready
# SIDENOTE: Call the 'def checkIfMembersLockedInSomeMethods(file_path : str):' function to check for the anti-pattern
from alerts import *
from typing import List
from formalCheckInterface import FormalCheckInterface
from Util import *
import clang.cindex

class Check(FormalCheckInterface):
	unlockedVar = list()	# Since we are using usr (unique symbol representations)
	lockedVar = list()		# we can and should make these global (for branching)

	def __init__(self):   
		self.inside = None  			#Check if we're in cxx method (class method)

		self.lock_guards = list()	
		self.locks = list()
		self.scopeLevel = 0

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		# If we're not in a class method we couldn't care less about what is accessed
		if self.inside != clang.cindex.CursorKind.CXX_METHOD:
			return
		
		#Checking for locks/unlock
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

		#We don't need to track mutexes, according to Gráinne's previous implementation
		#TODO figure out how to detect mutexs if included using non std namespace
		elif cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR and cursor.type.spelling != "std::mutex":
			newVar = Var(cursor)
			if self.locks or self.lock_guards:

				#Only need one example of it being locked to flag the error
				if newVar not in Check.lockedVar:
					Check.lockedVar.append(newVar)

				if newVar in Check.unlockedVar:
					newAlert = Alert(cursor.translation_unit, cursor.extent, 
						f"Data member '{cursor.displayname}' at (line: {cursor.extent.start.line}, column: {cursor.extent.start.column}) is accessed with a lock_guard or lock/unlock combination in this method, "+
						f"\nbut is not accessed with a lock_guard or lock/unlock combination in other methods\n "+
						f"Are you missing a lock_guard or lock/unlock combination in other methods which use '{cursor.displayname}'?", "error")
 
					if newAlert not in alerts:
						alerts.append(newAlert)
			else:
				#Only need one example of it being unlocked to flag the error
				if newVar not in Check.unlockedVar:
					Check.unlockedVar.append(newVar)

				if newVar in Check.lockedVar:

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
