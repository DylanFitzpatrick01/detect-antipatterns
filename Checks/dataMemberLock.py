import clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import FormalCheckInterface

"""
TODO Detect issues with data member that is accessed under a lock, but is also public so can be read/written directly. 
"""

class Check(FormalCheckInterface):
	def __init__(self):
		self.prevParents = list()
		# Only alert once per member!
		self.prevAlerts = list()
				
	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		# I think that this might detect the anti-pattern
		# No testing has been done.
		if cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
			if cursor.referenced.access_specifier == clang.cindex.AccessSpecifier.PUBLIC:
				# Mutex's are allowed to be public and naturally get accessed under a lock... Exclude them
				if cursor.type.spelling != "std::mutex" and cursor.type.spelling != "mutex":
					# Get base cursor of where this cursor is location.. go up
					c = findParent(self, cursor)

					if isScopeLocked(c, cursor.location):
						if cursor.spelling not in self.prevAlerts:
							self.prevAlerts.append(cursor.spelling)
							newAlert = Alert(cursor.translation_unit, cursor.location, "Warning: " + cursor.spelling + " is accessed"
																					 + " under a lock, while being public!", severity="warning")
							if newAlert not in alerts:
								alerts.append(newAlert)

		self.prevParents.append(cursor)
	
	

def findParent(self, child :clang.cindex.Cursor ) -> clang.cindex.Cursor:
	
	for c in self.prevParents:
		for i in c.walk_preorder():
			if i == child:
				return c
			
	return None

	# Is the scope within the extent of 'cursor' locked?
def isScopeLocked(cursor: clang.cindex.Cursor, loc: clang.cindex.SourceLocation) -> bool:
	# First figure out which line contains a lock
	lockPresent = False
	lockLine = None

	lockTypes = ["std::mutex", "mutex", "std::lock_guard<std::mutex>", "lock_guard<mutex>"]
	# RAII locks first:
	for c in cursor.walk_preorder():
		#print(str(c.location) + " " + str(c.type.spelling))
		if c.type.spelling in lockTypes:
			
			line = c.location.line
			if lockLine != None:
				lockLine = min(lockLine, line)
			else:
				lockLine = line
			if loc.line >= lockLine:
				lockPresent = True

	
	return lockPresent
		