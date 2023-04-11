import clang.cindex
class Function:
	def __init__(self, cursor: clang.cindex.Cursor):
		self.label = cursor.spelling

class Mutex:
	def __init__(self, cursor):
		self.file = str(cursor.location.file)
		self.line = str(cursor.location.line)
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

	def __eq__(self, __o: object) -> bool:
		if type(self) != type(__o):
			return False
		
		if self.mutex != __o.mutex:
			return False
		
		if self.file != __o.file:
			return False
		
		if self.line != __o.line:
			return False
		
		return True

	def copy(self):
		copy = Lock(self.cursor)

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

	def __eq__(self, __o: object) -> bool:
		if type(self) != type(__o):
			return False

		if self.mutex != __o.mutex:
			return False
		
		if self.file != __o.file:
			return False
		
		if self.line != __o.line:
			return False
		
		#TODO might not be possible
		if self.scopeLevel != __o.scopeLevel:
			return False
		
		return True
	
	def copy(self):
		copy = Lock_Guard(None, None)

		copy.cursor = self.cursor
		copy.mutex = self.mutex
		copy.file = self.file
		copy.line = self.line
		copy.scopeLevel = self.scopeLevel

		return copy

class Var:
	def __init__(self, cursor):
		self.cursor = cursor
		self.name = cursor.referenced.spelling
		self.usr = cursor.referenced.get_usr()
		self.file = cursor.location.file
		self.line = cursor.location.line

	def __eq__(self, __o: object) -> bool:
		if type(self) != type(__o):
			return False
		
		if self.usr != __o.usr:
			return False
		
		return True

class ConditionBodyStatement:
	def __init__(self, cursor):
		self.cursor = cursor
		self.compound_stmt = None

	
	def __setattr__(self, __name: str, __value) -> None:
		super().__setattr__(__name, __value)
