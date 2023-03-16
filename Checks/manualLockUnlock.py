import clang.cindex
from formalCheckInterface import *
from Util import Lock
from typing import List
from alerts import Alert

"""
A Check for a manual lock/unlock. If found issue a warning.
HOWEVER!! if we find a lock without an unlock, issue an error.#
Analyse_cursor() runs for EVERY cursor.
"""


#Note: No longer searches for locks/unlocks when COMPOUND_STMT recieved. Will
#      now just analyse given cursor -Leon Byrne
class Check(FormalCheckInterface):
	def __init__(self):
		self.locks = list()

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			if cursor.spelling == "lock" or cursor.spelling == "unlock":
				newAlert = Alert(cursor.translation_unit, cursor.location, "A manual lock/unlock is used, RAII is recommended", "warning")

				if newAlert not in alerts:
					alerts.append(newAlert)

			if cursor.spelling == "lock":
				self.locks.append(Lock(cursor))
			if cursor.spelling == "unlock":
				for lock in self.locks:
					if lock.mutex == list(list(cursor.get_children())[0].get_children())[0].spelling:
						self.locks.remove(lock)

	def __eq__(self, __o: object) -> bool:
		if type(self) != type(__o):
			return False
		
		if len(self.locks) != len(__o.locks):
			return False
		
		for i in range(0, len(self.locks)):
			if self.locks[i] != __o.locks[i]:
				return False
			
		return True

	# This is called when a scope is exited
	# Checking for locks then will tell us if there was a missing unlock
	def scope_decreased(self, alerts):
		for lock in self.locks:
			newAlert = Alert(lock.cursor.translation_unit, lock.cursor.location, "It's possible that this lock does not have a mathcing unlock within this scope")
				
			if newAlert not in alerts:
				alerts.append(newAlert)