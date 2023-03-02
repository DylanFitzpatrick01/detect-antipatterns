import clang.cindex

#Leon Byrne
#These are class for use with my locks.py file
#Could remove some and add some type variable instead

#TODO split orders down into just two mutexes, easier to check orders
#TODO maybe hold onto permutations of given orders too, adding one will give an error

class Scope:
	def __init__(self, scopeClass):
		self.data = []
		self.scopeClass = scopeClass
		self.parent = None

	def add(self, statement):
		self.data.append(statement)
		if type(statement) == Scope:
			statement.parent = self

class Function:
	def __init__(self, node, functionClass):
		self.node = node
		self.functionClass = functionClass

class Lock:
	def __init__(self, mutex, location):
		self.mutex = mutex
		self.location = location

class Unlock:
	def __init__(self, mutex, location):
		self.mutex = mutex
		self.location = location

class LockGuard:
	def __init__(self, mutex, location):
		self.mutex = mutex
		self.location = location

	
class Call:
	def __init__(self, function: Function, location):
		self.function = function
		self.location = location
		self.scope = Scope(function.functionClass)

class Locked:
	def __init__(self):
		self.order = []

	def lock(self, statement):
		error = False
		for lock in self.order:
			if lock.mutex == statement.mutex:
				error = True
		self.order.append(statement)
		return error

	#If this return false an error might occur as we are unlocking something that
	#we don't own, which may cause concurroncy errors
	def unlock(self, statement):
		removed = False
		for lock in self.order:
			if lock.mutex == statement.mutex:
				self.order.remove(lock)
				removed = True
		return removed
	
	def get_order(self):
		list = []
		for m in self.order:
			list.append(m.mutex)

		return list

class LockOrder:
	def __init__(self):
		self.orders = []

	def add(self, order):
		for i in range(len(order) - 1):
			for j in range(i + 1, len(order)):
				newOrder = [order[i], order[j]]
				if not newOrder in self.orders:
					self.orders.append(newOrder)
		
class WarningList():
	def __init__(self):
		self.warnings = list()

	def add(self, str):
		for w in self.warnings:
			if w == str:
				return
		self.warnings.append(str)

class Paths():
	def __init__(self):
		self.paths = list()
		self.nextPath = -1 #Look a get_next, explains why it starts at -1
	
	def copy(self):
		copy = Paths()
		copy.paths = self.paths.copy()

		return copy

	def add(self, newPath : bool):
		self.paths.append(newPath)

	def get_next(self):
		self.nextPath += 1
		return self.paths[self.nextPath]
	
	def has_next(self):
		return self.nextPath + 1 < len(self.paths)