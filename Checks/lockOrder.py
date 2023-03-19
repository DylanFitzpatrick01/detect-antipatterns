import clang.cindex
from alerts import *
from formalCheckInterface import *
from Util import Lock
from Util import Lock_Guard
from Util import Mutex

class Check(FormalCheckInterface):
	# orders is shared across all instances of this check
	orders = list()

	def __init__(self):
		self.locks = list()
		self.lock_guards = list()
		self.scopeLevel = 0

	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			if cursor.spelling == "lock":
				self.check_orders(cursor, alerts)
				self.locks.append(Lock(cursor))
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
			if lock.mutex == str(list(cursor.get_children())[0].referenced.get_usr()):
				alreadyHeld = True

		for lock in self.lock_guards:
			if lock.mutex == str(list(cursor.get_children())[0].referenced.get_usr()):
				alreadyHeld = True

		if not alreadyHeld:
			if cursor.spelling == "lock":
				new = Mutex(list(cursor.get_children())[0])
			else:
				new = Mutex(cursor)

			for lock in self.locks:
				newOrder = [Mutex(list(lock.cursor.get_children())[0]), new]

				notPresent = True
				for order in Check.orders:
					if newOrder[0] == order[0] and newOrder[1] == order[1]:
						notPresent = False

					if newOrder[0] == order[1] and order[0] == newOrder[1]:
						notPresent = False

						newAlert = Alert(cursor.translation_unit, cursor.extent, (
	 								"Locking order may cause deadlock.\n" + 
									"Locked: " + order[0].name + " in: " + order[0].file + " at line: " + order[0].line + "\n" +
									"Locked: " + order[1].name + " in: " + order[1].file + " at line: " + order[1].line + "\n" +
									"\n" +
									"Locked: " + newOrder[0].name + " in: " + newOrder[0].file + " at line: " + newOrder[0].line + "\n" +
									"Locked: " + newOrder[1].name + " in: " + newOrder[1].file + " at line: " + newOrder[1].line + "\n"))
								
						if newAlert not in alerts:
							alerts.append(newAlert)
				
				if notPresent:
					Check.orders.append(newOrder)
					
			for lock in self.lock_guards:
				newOrder = [Mutex(lock.cursor), new]

				notPresent = True
				for order in Check.orders:
					if newOrder[0] == order[0] and newOrder[1] == order[1]:
						notPresent = False

					if newOrder[0] == order[1] and order[0] == newOrder[1]:
						notPresent = False

						newAlert = Alert(cursor.translation_unit, cursor.extent, (
	 								"Locking order may cause deadlock.\n" + 
									"Locked: " + order[0].name + " in: " + order[0].file + " at line: " + order[0].line + "\n" +
									"Locked: " + order[1].name + " in: " + order[1].file + " at line: " + order[1].line + "\n" +
									"\n" +
									"Locked: " + newOrder[0].name + " in: " + newOrder[0].file + " at line: " + newOrder[0].line + "\n" +
									"Locked: " + newOrder[1].name + " in: " + newOrder[1].file + " at line: " + newOrder[1].line + "\n"))
								
						if newAlert not in alerts:
							alerts.append(newAlert)
				
				if notPresent:
					Check.orders.append(newOrder)
					
	def __eq__(self, __o: object) -> bool:
		if type(self) != type(__o):
			return False

		#The numbers can only change if new lock guard made
		if len(self.lock_guards) != len(__o.lock_guards):
			return False
		
		for i in range(0, len(self.lock_guards)):
			if not self.lock_guards[i].equals(__o.lock_guards[i]):
				return False

		if len(self.locks) != len(__o.locks):
			return False
		
		for i in range(0, len(self.locks)):
			if self.locks[i] != __o.locks[i]:
				return False
			
		return True
	
	def copy(self):
		copy = Check()

		for lockGuard in self.lock_guards:
			copy.lock_guards.append(lockGuard.copy())

		for lock in self.locks:
			copy.locks.append(lock.copy())

		copy.scopeLevel = self.scopeLevel

		return copy
			
	def scope_increased(self, alerts):
		self.scopeLevel += 1
	
	def scope_decreased(self, alerts):
		self.scopeLevel -= 1
								
		for lockGuard in self.lock_guards:
			if lockGuard.scopeLevel >= self.scopeLevel:
				self.lock_guards.remove(lockGuard)

	def new_function(self, cursor, alerts):
		self.locks = list()
		self.lock_guards = list()  
		self.scopeLevel = 0