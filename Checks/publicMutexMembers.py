import clang.cindex
from alerts import Alert

"""
TODO Write Description
"""

class Check():
	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if str(cursor.access_specifier) == "AccessSpecifier.PUBLIC":
				count = 0
				contains = False
				for cursor1 in cursor.get_children():
					count += 1
					if str(cursor1.displayname) == "class std::mutex" and str(cursor1.kind) == "CursorKind.TYPE_REF":
						contains = True
					if count > 2:
						break
				if contains and count == 2:
					alerts.append(Alert(cursor.translation_unit, cursor.extent,
											"Are you sure you want to have a public mutex called '" + cursor.displayname + "'?\n"
											"Consider making this mutex private."))
	
		
	def copy(self):
		#TODO evaluate whether the copy needs an data to be passed on
		return Check()
	
	def equal_state(self, other):
		#TODO evaluate whether this and tother might have differing data
		return True
			
	#Checks may not implement this unless they need to
	def scope_increased(self):
		pass

	# Check may not implement this unless they need to
	def scope_decreased(self):
		pass