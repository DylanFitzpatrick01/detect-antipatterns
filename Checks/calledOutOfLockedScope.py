from formalCheckInterface import *
from typing import List

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
				msg = "Called out of locked scope in file: " + str(cursor.location.file) + " at: " + str(cursor.location.line)

				for lock in self.locks:
					msg = msg + "\n  " + lock.mutex + " is locked in: " + lock.file + " at: " + lock.line

				for lock_guard in self.lock_gaurds:
					msg = msg + "\n  " + lock_guard.mutex + " is locked in: " + lock_guard.file + " at: " + lock_guard.line

				for alert in alerts:
					if msg == alert.message:
						return

				alerts.append(Alert(cursor.translation_unit, cursor.extent, msg))

	def equal_state(self, other) -> bool:
		#The numbers can only change if new lock guard made
		if len(self.lock_gaurds) != len(other.lock_guards):
			return False
		
		for i in range(0, len(self.locks)):
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
		for lockGuard in self.lock_gaurds:
			if lockGuard.scopeLevel == self.scopeLevel:
				self.lock_gaurds.remove(lockGuard)

		self.scopeLevel -= 1

class Lock:
	def __init__(self, cursor):
		if cursor is None:
			pass
		else:
			self.mutex = str(list(list(cursor.get_children())[0].get_children())[0].spelling)
			self.file = str(cursor.location.file)
			self.line = str(cursor.location.line)

	def equals(self, other) -> bool:
		if self.mutex != other.mutex:
			return False
		
		if self.file != other.file:
			return False
		
		if self.line != other.line:
			return False
		
		return True

	def copy(self):
		copy = Lock()

		copy.mutex = self.mutex
		copy.file = self.file
		copy.line = self.line

		return copy

class Lock_Guard:
	def __init__(self, cursor, scopeLevel):
		#TODO implement this
		#Store data as strings, cursors hanve different pointers even if same data
		if cursor is None or scopeLevel is None:
			pass
		else:
			self.mutex = str(list(cursor.get_children())[0].spelling)
			self.file = str(cursor.location.file)
			self.line = str(cursor.location.line)
			self.scopeLevel = scopeLevel

	def equals(self, other) -> bool:
		if self.mutex != other.mutex:
			return False
		
		if self.file != other.file:
			return False
		
		if self.line != other.line:
			return False
		
		#TODO might not be possible
		if self.scopeLevel != other.scopeLevel:
			return False
		
		return True
	
	def copy(self):
		copy = Lock_Guard(None, None)

		copy.mutex = self.mutex
		copy.file = self.file
		copy.line = self.line
		copy.scopeLevel = self.scopeLevel

		return copy
