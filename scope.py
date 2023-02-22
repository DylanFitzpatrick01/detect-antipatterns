#Leon Byrne
#These are class for use with my locks.py file
#Could remove some and add some type variable instead

#TODO split orders down into just two mutexes, easier to check orders
#TODO maybe hold onto permutations of given orders too, adding one will give an error

class Scope:
	def __init__(self, scopeClass):
		self.data = []
		self.scopeClass = scopeClass

	def add(self, statement):
		self.data.append(statement)

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
		if not order in self.orders and len(order) > 1:
			self.orders.append(order)

		for i in range(len(order) - 1):
			for j in range(i + 1, len(order)):
				newOrder = [order[i], order[j]]
				if not newOrder in self.orders:
					self.orders.append(newOrder)
		