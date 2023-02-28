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

	def get_non_empty(self):
		returned = None
		for a in self.data:
			if type(a) != Scope:
				return self
			else:
				if returned == None:
					if a.get_non_empty() != None:
						returned = a.get_non_empty
				else:
					if a.get_non_empty() != None:
						return self
		
		return returned

	def empty(self):
		for a in self.data:
			if type(a) != Scope:
				return False
			else:
				if not a.empty():
					return False

		return True 

	def contains(self, object):
		for a in self.data:
			if a == object:
				return True
			elif type(a) == Scope:
				if a.contains(object):
					return True
		return False

	#Returns the root of a given scope
	def get_scope_root(self):
		if self.parent != None:
			return self.parent.get_scope_root()
		else:
			return self

	#gets the rightest, or the last added scope
	def get_rightest_leaf(self):
		#I don't know why but if len is 1 the for loop below is skipped
		#Weird but not an impossible fix
		#
		#No, this annoyed me to no end. I may be stupid but why?
		#-Leon Byrne
		if len(self.data) == 1 and type(self.data[0]) == Scope:
			return self.data[0].get_rightest_leaf()

		for i in range(len(self.data) - 1, -1, -1):
			if type(self.data[i]) == Scope:
				return self.data[i].get_rightest_leaf()
		return self

	#Copies the root node and all other nodes downwards
	def root_copy(self):
		copy = Scope(self.scopeClass)

		for a in self.data:
			if type(a) == Scope:
				copy.add(a.root_copy())
			else:
				#No need to copy lock objects and such. Reference will do
				copy.add(a)
		return copy

	#Copies the node's root and returns this copy afterwards
	def copy(self):
		rootCopy = self.get_scope_root().root_copy()
		return rootCopy.get_rightest_leaf()

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

def node_contains(root, node, func):
	if root == node:
		return True
	elif root.kind == clang.cindex.CursorKind.CALL_EXPR and root.spelling in func:
		if node_contains(func[root.spelling].node, node, func):
			return True
	else:
		for child in root.get_children():
			if node_contains(child, node, func):
				return True
	return False
		
class WarningList():
	def __init__(self):
		self.warnings = list()

	def add(self, str):
		for w in self.warnings:
			if w == str:
				return
		self.warnings.append(str)