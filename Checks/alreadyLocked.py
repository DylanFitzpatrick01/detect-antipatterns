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
				newLock = Lock(cursor)

				msg = ""
				for lock in self.locks:
					if lock.mutex == list(list(cursor.get_children())[0].get_children())[0].referenced.get_usr():
						msg += "\n  " + lock.mutexName + " is locked in: " + lock.file + " at: " + lock.line

				if msg != "":
					mutex = str(list(list(cursor.get_children())[0].get_children())[0].spelling)
					newAlert = Alert(cursor.translation_unit, cursor.extent, mutex + " might already be locked" + msg)

					if newAlert not in alerts:
						alerts.append(newAlert)

				self.locks.append(newLock)
			elif cursor.spelling == "unlock":
				for lock in self.locks:
					# If the referenced mutex of the unlock matches the lock, remove the lock
					if lock.mutex == list(list(cursor.get_children())[0].get_children())[0].referenced.get_usr():
						self.locks.remove(lock)
			elif cursor.spelling == "lock_guard":
				self.lock_guards.append(Lock_Guard(cursor, self.scopeLevel))
		
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