import clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import FormalCheckInterface

"""
TODO Write Description
"""
# We only want to run the check once!
checked = False

class Check(FormalCheckInterface):
	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		global checked
		
		

		# If we haven't run the check before...
		if (not checked):
			joinDetected = 0
			joinableDetected = 0

			for node in  cursor.translation_unit.cursor.walk_preorder():
				if node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "join" and node.type.spelling == "void": 
					joinDetected += 1
					#print("Found std::thread::join() function call at line {0}".format(node.location.line))
				elif (node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "joinable" and node.type.spelling == "bool"):
					joinableDetected += 1
					#print("Found std::thread::joinable() function call at line {0}".format(node.location.line))


			if joinDetected != joinableDetected:
				newAlert = Alert(cursor.translation_unit, cursor.extent,"Not all join functions are checked if thread is joinable")
				if newAlert not in alerts:
					alerts.append(newAlert)

			# Set the 'checked' flag, so we don't run this check again.
			checked = True