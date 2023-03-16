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


		# if (cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT):
		# 	lock_caller = find_caller(cursor, "lock")
		# 	unlock_caller = find_caller(cursor, "unlock")
		# 	if (lock_caller and unlock_caller):
		# 		alerts.append(Alert(cursor.translation_unit, cursor.extent,
		# 								"A manual lock/unlock is used in this scope.\n" 
		# 								"It's reccommended you use an RAII locking scheme, i.e.\n"
		# 								"remove '" + lock_caller + ".unlock();' and replace '" + lock_caller + ".lock();' with\n"
		# 								"'std::lock_guard<std::mutex> lock(" + lock_caller + ");'", "warning"))
		# 	if (lock_caller and not unlock_caller):
		# 		alerts.append(Alert(cursor.translation_unit, cursor.extent,
		# 								"A manual lock is used in this scope without an unlock!.\n"
		# 								"Please either replace '" + lock_caller + ".lock();' with 'std::lock_guard<std::mutex> lock(" + lock_caller + ");' (RECCOMMENDED),\n"
		# 								"or add '" + lock_caller + ".unlock();' at the end of this critical section."))						 

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

				
# Given a function name 'func', if "class.func()" is found, return class.
def find_caller(cursor:clang.cindex.Cursor, name):
	toks = list(cursor.get_tokens())
	for i in range (len(toks)):
		if(toks[i].spelling == name and toks[i-1].spelling == "."):
			return toks[i-2].spelling