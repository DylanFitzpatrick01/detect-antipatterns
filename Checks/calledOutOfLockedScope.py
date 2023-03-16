from formalCheckInterface import *
from typing import List
from Util import *

class Check(FormalCheckInterface):
	def __init__(self):
		self.lock_guards = list()	
		self.locks = list()
		self.scopeLevel = 0

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
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
			elif self.locks or self.lock_guards:
				# If there is a call that is not a .lock(), .unlock() or lock_guard and
				# there are still held mutexes (the lists not being empty) raise an
				# error and inform of which call was made and which mutex/es are locked.
				msg = "Called: " + str(cursor.referenced.spelling) + " out of locked scope"
				for lock in self.locks:
					msg = msg + "\n  " + lock.mutexName + " is locked in: " + lock.file + " at: " + lock.line

				for lock_guard in self.lock_guards:
					msg = msg + "\n  " + lock_guard.mutexName + " is locked in: " + lock_guard.file + " at line: " + lock_guard.line

				newAlert = Alert(cursor.translation_unit, cursor.extent, msg)

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
	def new_function(self, alerts):
		self.lock_guards = list()
		self.locks = list()
		self.scopeLevel = 0