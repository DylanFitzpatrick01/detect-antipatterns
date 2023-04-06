from formalCheckInterface import FormalCheckInterface
from alerts import Alert
import clang.cindex

class Check(FormalCheckInterface):
	def __init__(self):
		self.affected = dict()      # Dict of atomics and lists of affected vars
		self.investagating = None		
		self.skipNext = False

		self.references = list()

		self.atomicWrite = False
		self.affectedSeen = 0

		self.branchLevel = 0        # The level of branches we're in. 0 is none, >1
																# is a nested branch

	# When a var will be changed, add it to the stack. When moved on, remove it
	# If entered method tell it next return

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if cursor.location.line == 19:
			print("at the problem area")

		if cursor.kind == clang.cindex.CursorKind.VAR_DECL or cursor.kind == clang.cindex.CursorKind.FIELD_DECL:
			if "std::atomic" in cursor.type.spelling:
				self.affected[cursor.referenced.get_usr()] = list()
			else:
				self.investigate_new(cursor)

		elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR and "operator" in cursor.spelling:
			# print(cursor.spelling)
			if "atomic" in list(cursor.get_children())[0].type.spelling:
				self.atomicWrite = True
				self.investigate_new(list(cursor.get_children())[0])
				self.skipNext = True

		# This is some bullshit, so binary operators have an "operator type" cursor
		# under them. Variables with operator in them will not be detected.
		elif cursor.kind == clang.cindex.CursorKind.BINARY_OPERATOR and "operator" not in list(cursor.get_children())[0].spelling:
			print("Binary ", list(cursor.get_children())[0].spelling)
			self.atomicWrite = False
			self.investigate_new(list(cursor.get_children())[0])
			self.skipNext = True 


		elif cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR or cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
			# Atomic to atomic writes are okay, don't investigate
			# print(cursor.referenced.type.spelling)
			if "std::atomic" in cursor.referenced.type.spelling and "std::atomic" not in self.investagating.referenced.type.spelling:
				print(self.investagating.referenced.type.spelling)
				self.affected[cursor.referenced.get_usr()].append(self.investagating.referenced)
				self.affectedSeen += 1
			elif not self.skipNext:
				if self.atomicWrite:
					for key in self.affected:
						for var in self.affected[key]:
							if cursor.referenced.get_usr() == var.get_usr():
								self.atomicWrite = False
								
								newAlert = Alert(self.investagating.translation_unit, self.investagating.extent, 
																 "This appears to be the end of a non-atomic series of operations.")
								if newAlert not in alerts:
									alerts.append(newAlert)
								print("error")
				else:
					for key in self.affected:
						for var in self.affected[key]:
							if cursor.referenced.get_usr() == var.get_usr() and "__atomic" not in self.investagating.type.spelling and self.investagating.referenced not in self.affected[key]:
								print(cursor.referenced.type.spelling)
								
								self.affected[key].append(self.investagating.referenced)
								self.affectedSeen += 1
			elif self.skipNext:
				self.skipNext = False

		# for key in self.affected:
		#   print(key)
		#   for var in self.affected[key]:
		#     print("  ", var.get_usr())

	def investigate_new(self, cursor):
		if self.affectedSeen == 0:
			self.remove_affected(self.investagating)

		self.affectedSeen = 0
		self.investagating = cursor

	def remove_affected(self, cursor):
		for key in self.affected:
			for var in self.affected[key]:
				if cursor.referenced.get_usr() == var.get_usr():
					self.affected[key].remove(var)

	# def check_references(self):
	# 	#TODO if one of the references is an atomic or atomic affected, add to the 
	# 	# 		dict. If none of them are remove it.
	# 	#			clear out references afterwards.
	# 	atomicRef = False

	# 	for reference in self.references:
	# 		if key in self.affected:
	# 			if reference.referenced.get_usr() in self.affected[key]:
	# 				if self.investagating.referenced.get_usr() not in self.affected[key]:
	# 					self.affected[key].append(self.investagating.get_usr())
			
	# 		elif "std::atomic" in reference.referenced.type.spelling: 
	# 			atomicRef = True
	# 			if self.investagating not in self.affected[reference.referenced.get_usr()]:
	# 				self.affected[reference.referenced.get_usr()].append(self.investagating.get_usr())

	# 	if not atomicRef:
	# 		# remove investigating from affected
	# 		for key in self.affected:
	# 			self.affected[key].delete(self.investagating.referenced.get_usr())

	# 	self.references = list()

	def __eq__(self, __o: object) -> bool:
		if type(self) != type(__o):
			return False

		if self.affected != __o.affected:
			return False
		
		return True