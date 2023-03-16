import clang.cindex
from alerts import *
from formalCheckInterface import *
from Util import Lock
from Util import Lock_Guard
from Util import Mutex

class Check(FormalCheckInterface):
	def __init__(self):
		self.locks = list()
		self.lock_guards = list()
		self.scopeLevel = 0
		self.orders = list() # list of list of Mutexes

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			if cursor.spelling == "lock":
				self.check_orders(cursor, alerts)
				self.locks.append(Lock(cursor))

				newMutex = True
			elif cursor.spelling == "unlock":
				for lock in self.locks:
					# Use .get_usr() it will differenciate between different mutexes of 
					# the same name.
					if lock.mutex == str(list(list(cursor.get_children())[0].get_children())[0].get_usr()):
						self.locks.remove(lock)
			elif cursor.spelling == "lock_guard":
				self.check_orders(cursor, alerts)
				self.lock_guards.append(Lock_Guard(cursor, self.scopeLevel))


	def check_orders(self, cursor, alerts):
		alreadyHeld = False

		for lock in self.locks:
			# print(lock.mutex)
			# print(list(cursor.get_children())[0].spelling)
			# print(str(list(cursor.get_children())[0].referenced.get_usr()))
			# print()
			if lock.mutex == str(list(cursor.get_children())[0].referenced.get_usr()):
				alreadyHeld = True

		for lock in self.lock_guards:
			# print(lock.mutex)
			# print(list(cursor.get_children())[0].spelling)
			# print(str(list(cursor.get_children())[0].referenced.get_usr()))
			# print()
			if lock.mutex == str(list(cursor.get_children())[0].referenced.get_usr()):
				alreadyHeld = True

		if not alreadyHeld:
			new  = Mutex(cursor)

			for lock in self.locks:
				newOrder = [Mutex(lock.cursor), Mutex(cursor)]

				notPresent = True
				for order in self.orders:
					if newOrder[0] == order[0] and newOrder[1] == order[1]:
						notPresent = False

					if newOrder[0] == order[1] and order[0] == newOrder[1]:
						notPresent = False

						newAlert = Alert(cursor.translation_unit, cursor.extent, (
	 								"Locking order may cause deadlock.\n" + 
									"Locked: " + order[0].name + " in: " + order[0].file + " at line: " + order[0].line + "\n" +
									"        " + order[1].name + " in: " + order[1].file + " at line: " + order[1].line + "\n" +
									"\n" +
									"Locked: " + newOrder[0].name + " in: " + newOrder[0].file + " at line: " + newOrder[0].line + "\n" +
									"        " + newOrder[1].name + " in: " + newOrder[1].file + " at line: " + newOrder[1].line + "\n"))
								
						alertPresent = False
						for alert in alerts:
							if alert.equal(newAlert):
								alertPresent = True

						if not alertPresent:
							alerts.append(newAlert)
				
				if notPresent:
					self.orders.append(newOrder)
					
			for lock in self.lock_guards:
				newOrder = [Mutex(lock.cursor), Mutex(cursor)]

				notPresent = True
				for order in self.orders:
					if newOrder[0] == order[0] and newOrder[1] == order[1]:
						notPresent = False

					if newOrder[0] == order[1] and order[0] == newOrder[1]:
						notPresent = False

						newAlert = Alert(cursor.translation_unit, cursor.extent, (
	 								"Locking order may cause deadlock.\n" + 
									"Locked: " + order[0].name + " in: " + order[0].file + " at line: " + order[0].line + "\n" +
									"        " + order[1].name + " in: " + order[1].file + " at line: " + order[1].line + "\n" +
									"\n" +
									"Locked: " + newOrder[0].name + " in: " + newOrder[0].file + " at line: " + newOrder[0].line + "\n" +
									"        " + newOrder[1].name + " in: " + newOrder[1].file + " at line: " + newOrder[1].line + "\n"))
								
						alertPresent = False
						for alert in alerts:
							if alert.equal(newAlert):
								alertPresent = True

						if not alertPresent:
							alerts.append(newAlert)
				
				if notPresent:
					self.orders.append(newOrder)
					


	def equal_state(self, other) -> bool:
		if not super().equal_state(other):
			return False

		#The numbers can only change if new lock guard made
		if len(self.lock_guards) != len(other.lock_guards):
			return False
		
		for i in range(0, len(self.lock_guards)):
			if not self.lock_guards[i].equals(other.lock_guards[i]):
				return False

		if len(self.locks) != len(other.locks):
			return False
		
		for i in range(0, len(self.locks)):
			if not self.locks[i].equals(other.locks[i]):
				return False
			
		if len(self.orders) != len(other.orders):
			return False
		
		for i in range(0, len(self.orders)):
			if not self.orders[i][0] == other.orders[i][0]:
				return False
			
			if not self.orders[i][1] == other.orders[i][1]:
				return False
			
		return True
	
	def copy(self):
		copy = Check()

		for lockGuard in self.lock_guards:
			copy.lock_guards.append(lockGuard.copy())

		for lock in self.locks:
			copy.locks.append(lock.copy())

		copy.scopeLevel = self.scopeLevel

		for order in self.orders:
			copy.orders.append(order)

		return copy
			
	def scope_increased(self, alerts):
		self.scopeLevel += 1
	
	def scope_decreased(self, alerts):
		self.scopeLevel -= 1
								
		for lockGuard in self.lock_guards:
			if lockGuard.scopeLevel >= self.scopeLevel:
				self.lock_guards.remove(lockGuard)

	def new_function(self, alerts):
		self.locks = list()
		self.lock_guards = list()  