from formalCheckInterface import *
from typing import List
from Util import *

class Check(FormalCheckInterface):
	def __init__(self):
		self.lock_gaurds = list()	
		self.locks = list()
		self.scopeLevel = 0

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			if cursor.spelling == "lock":
				self.locks.append(Lock(cursor))
			elif cursor.spelling == "unlock":
				for lock in self.locks:
					if lock.mutex == list(list(cursor.get_children())[0].get_children())[0].spelling:
						self.locks.remove(lock)
			elif cursor.spelling == "lock_guard":
				self.lock_gaurds.append(Lock_Guard(cursor, self.scopeLevel))
			elif self.locks or self.lock_gaurds:
				msg = "Called: " + str(cursor.spelling) + " out of locked scope"
				for lock in self.locks:
					msg = msg + "\n  " + lock.mutex + " is locked in: " + lock.file + " at: " + lock.line

				for lock_guard in self.lock_gaurds:
					msg = msg + "\n  " + lock_guard.mutex + " is locked in: " + lock_guard.file + " at: " + lock_guard.line

				newAlert = Alert(cursor.translation_unit, cursor.extent, msg)
				for alert in alerts:
					if alert.equal(newAlert):
						return

				alerts.append(newAlert)

	def equal_state(self, other) -> bool:
		if not super().equal_state(other):
			return False

		#The numbers can only change if new lock guard made
		if len(self.lock_gaurds) != len(other.lock_gaurds):
			return False
		
		for i in range(0, len(self.lock_gaurds)):
			if not self.lock_gaurds[i].equals(other.lock_guards[i]):
				return False

		if len(self.locks) != len(other.locks):
			return False
		
		for i in range(0, len(self.locks)):
			if not self.locks[i].equals(other.locks[i]):
				return False
			
		return True

	def copy(self):
		copy = Check()

		for lockGuard in self.lock_gaurds:
			copy.lock_gaurds.append(lockGuard.copy())

		for lock in self.locks:
			copy.locks.append(lock.copy())

		copy.scopeLevel = self.scopeLevel

		return copy
	
	def scope_increased(self):
		self.scopeLevel += 1

	# Removes all Lock_Guards in the current scope before movinng back to a lesser
	# scope
	def scope_decreased(self):

		self.scopeLevel -= 1
		for lockGuard in self.lock_gaurds:
			if lockGuard.scopeLevel >= self.scopeLevel:
				self.lock_gaurds.remove(lockGuard)

	def new_function(self):
		self.lock_gaurds = list()
		self.locks = list()
		self.scopeLevel = 0