import clang.cindex

class Function:
	def __init__(self, cursor: clang.cindex.Cursor):
		self.label = cursor.spelling

class Mutex:
	def __init__(self, cursor):
		self.file = str(cursor.location.file)
		self.line = str(cursor.location.file)
		self.name = str(list(cursor.get_children())[0].spelling)
		self.usr = str(list(cursor.get_children())[0].referenced.get_usr())

	def __eq__(self, __o: object) -> bool:
		return type(self) == type(__o) and self.usr == __o.usr

class Lock:
	def __init__(self, cursor):
		if cursor is None:
			pass
		else:
			self.cursor = cursor
			self.mutex = str(list(list(cursor.get_children())[0].get_children())[0].referenced.get_usr())
			self.mutexName = str(list(list(cursor.get_children())[0].get_children())[0].spelling)
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
			self.cursor = cursor
			self.mutex = str(list(cursor.get_children())[0].referenced.get_usr())
			self.mutexName = str(list(cursor.get_children())[0].spelling)
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
