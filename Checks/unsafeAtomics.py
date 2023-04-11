from formalCheckInterface import FormalCheckInterface
from alerts import Alert
import clang.cindex

class Check(FormalCheckInterface):
	def __init__(self):
		self.affected = dict()      # Dict of atomics and lists of affected vars
		self.investagating = None
		self.skipNext = False

		self.atomic = None
		self.isFetch = False				# If fetch call, only counter members

		self.references = list()

		self.atomicWrite = False
		self.affectedSeen = 0

	# When a var will be changed, add it to the stack. When moved on, remove it
	# If entered method tell it next return

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if cursor.referenced is not None and cursor.referenced.type is not None and "std::atomic" in cursor.referenced.type.spelling and cursor.referenced.get_usr() not in self.affected:
			self.affected[cursor.referenced.get_usr()] = list()

		if cursor.kind == clang.cindex.CursorKind.VAR_DECL or cursor.kind == clang.cindex.CursorKind.FIELD_DECL:
			if "std::atomic" not in cursor.type.spelling:
				self.atomicWrite = False
				self.investigate_new(cursor)
				self.skipNext = False

				self.isFetch = False

		# atomic types such as atomic int can use operators such as &= and +=
		elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR and "operator" in cursor.spelling:
			if "atomic" in list(cursor.get_children())[0].type.spelling:
				self.atomicWrite = True

				self.atomic = list(cursor.get_children())[0]

				self.investigate_new(list(cursor.get_children())[0])
				self.skipNext = True

				self.isFetch = False


		elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR and "store" in cursor.spelling:
			if "atomic" in list(list(cursor.get_children())[0].get_children())[0].type.spelling:
				self.atomicWrite = True
				self.atomic = list(list(cursor.get_children())[0].get_children())[0]
				self.skipNext = True

				self.isFetch = False

		# Some fetch type calls can both access and modify atomic values, it must be
		# handled differently to reflect that.
		elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR and ("fetch" in cursor.spelling or "exchange" in cursor.spelling):
			if "atomic" in list(list(cursor.get_children())[0].get_children())[0].type.spelling:
				self.atomicWrite = True
				self.atomic = list(list(cursor.get_children())[0].get_children())[0]
				self.skipNext = True

				self.isFetch = True

		# Some fetch type calls can both access and modify atomic values, it must be
		# handled differently to reflect that.
		elif cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR and ("fetch" in cursor.spelling or "exchange" in cursor.spelling):
			if "atomic" in list(cursor.get_children())[0].type.spelling:
				self.atomicWrite = True
				self.atomic = list(cursor.get_children())[0]
				self.skipNext = True

				self.isFetch = True

		# Call expressions are a limit of this check. We don't check what is passed
		# or returned. They can be a source for false negatives.
		elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			self.atomic = None
			self.investigate_new(None)

		# This is some bullshit, some binary operators have an "operator type"
		# cursor under them, this screws stuff up. To fix this no variables with
		# operator in their name will be checked.
		elif cursor.kind == clang.cindex.CursorKind.BINARY_OPERATOR and "operator" not in list(cursor.get_children())[0].spelling:
			if list(cursor.get_children())[0].spelling != '':
				self.atomicWrite = False
				self.investigate_new(list(cursor.get_children())[0])
				self.skipNext = True

				self.isFetch = False

		elif cursor.kind == clang.cindex.CursorKind.UNARY_OPERATOR:
			self.atomicWrite = False

		elif cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR or cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
			if self.investagating is not None:
				if "std::atomic" not in self.investagating.referenced.type.spelling: 
					if "std::atomic" in cursor.referenced.type.spelling:
						self.affected[cursor.referenced.get_usr()].append(self.investagating.referenced)
						self.affectedSeen += 1
				elif not (self.skipNext or self.isFetch):
					for key in self.affected:
						for val in self.affected[key]:
							if cursor.referenced.get_usr() == val.get_usr():
								val.append(self.investagating.referenced)
								self.affectedSeen += 1
				elif self.skipNext:
					self.skipNext = False

			if self.atomic is not None and self.atomicWrite:
				for val in self.affected[self.atomic.referenced.get_usr()]:
					if val.get_usr() == cursor.referenced.get_usr():
						newAlert = Alert(self.atomic.translation_unit, self.atomic.extent,
														 "This appears to be the end of a non-atomic series of operations.\n" +
														 "Consider protecting \"" + self.atomic.spelling + "\" with a mutex.")
						if newAlert not in alerts:
							alerts.append(newAlert)

			
			# Atomic to atomic writes are okay, don't investigate
			# if self.investagating is not None and "std::atomic" in cursor.referenced.type.spelling and "std::atomic" not in self.investagating.referenced.type.spelling:
			# 	self.affected[cursor.referenced.get_usr()].append(self.investagating.referenced)
			# 	self.affectedSeen += 1
			# elif not self.skipNext:
			# 	if self.atomicWrite and self.atomic is not None:
			# 		for key in self.affected:
			# 			for var in self.affected[key]:
			# 				if cursor.referenced.get_usr() == var.get_usr():
			# 					self.atomicWrite = False

			# 					newAlert = Alert(self.atomic.translation_unit, self.atomic.extent,
			# 													 "This appears to be the end of a non-atomic series of operations.\n" +
			# 													 "Consider protecting \"" + self.atomic.spelling + "\" with a mutex.")
			# 					if newAlert not in alerts:
			# 						alerts.append(newAlert)
			# 	elif not self.isFetch or "std::atomic" in cursor.referenced.kind.spelling:
			# 		for key in self.affected:
			# 			for var in self.affected[key]:
			# 				if self.investagating is not None and cursor.referenced.get_usr() == var.get_usr() and "__atomic" not in self.investagating.type.spelling and self.investagating.referenced not in self.affected[key]:
			# 					self.affected[key].append(self.investagating.referenced)
			# 					self.affectedSeen += 1
			# elif self.skipNext:
			# 	self.skipNext = False

	def investigate_new(self, cursor):
		if self.affectedSeen == 0 and self.investagating is not None:
			self.remove_affected(self.investagating)

		self.affectedSeen = 0


		self.investagating = cursor

	def remove_affected(self, cursor):
		for key in self.affected:
			for var in self.affected[key]:
				if cursor.referenced.get_usr() == var.get_usr():
					self.affected[key].remove(var)

	def __eq__(self, __o: object) -> bool:
		if type(self) != type(__o):
			return False

		for key in self.affected:
			if key not in __o.affected:
				return False

			for val in self.affected[key]:
				if val not in __o.affected[key]:
					return False

		for key in __o.affected:
			if key not in self.affected:
				return False

			for val in __o.affected[key]:
				if val not in self.affected[key]:
					return False

		return True