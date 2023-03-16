import clang.cindex
from alerts import *
from formalCheckInterface import *
from Util import Lock

"""
A Check for a manual lock/unlock. If found issue a warning.
HOWEVER!! if we find a lock without an unlock, issue an error.#
Analyse_cursor() runs for EVERY cursor.
"""

class Check(FormalCheckInterface):
	def __init__(self):
		self.locks = list()

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			if cursor.spelling == "lock" or cursor.spelling == "unlock":
				newAlert = Alert(cursor.translation_unit, cursor.location, "A manual lock/unlock is used, RAII is recommended", "warning")

				present = False
				for alert in alerts:
					#If an alert is in the same location, the alert is already recorded
					if alert.equal(newAlert):
						present = True
				
				if not present:
					alerts.append(newAlert)

			if cursor.spelling == "lock":
				self.locks.append(Lock(cursor))
			if cursor.spelling == "unlock":
				for lock in self.locks:
					if lock.mutex == list(list(cursor.get_children())[0].get_children())[0].spelling:
						self.locks.remove(lock)

	# This is called when a scope is exited
	# Checking for locks then will tell us if there was a missing unlock
	def scope_decreased(self, alerts):
		for lock in self.locks:
			newAlert = Alert(lock.cursor.translation_unit, lock.cursor.location, "It's possible that this lock does not have a mathcing unlock within this scope")
				
			present = False
			for alert in alerts:
				#If an alert is in the same location, the alert is already recorded
				if alert.equal(newAlert):
					present = True
				
			if not present:
				alerts.append(newAlert)