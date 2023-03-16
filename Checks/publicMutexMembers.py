import clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import *

"""
TODO Write Description
"""

class Check(FormalCheckInterface):
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
					newAlert = Alert(cursor.translation_unit, cursor.extent,
											"Are you sure you want to have a public mutex called '" + cursor.displayname + "'?\n"
											"Consider making this mutex private.")
					
					for alert in alerts:
						if alert.equal(newAlert):
							return
					
					alerts.append(newAlert)
	
