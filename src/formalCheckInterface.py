import abc
import clang.cindex
from typing import List
from alerts import Alert

# Guide
# In order to make a new check, simply have it inherit from FormalCheckInterface
# this will let it inherit all the methods from here and be used in traverse.
#
# When adding a new alert use:
#		if newAlert not in alerts:		This avoids the issue of duplicate alerts
#			alerts.append(newAlert)
#
# If you have some state that needs to be saved and used while running (eg what
# mutexes are currently locked) simply override the __init__ function and add
# any needed variable to it.Check the Util.py file. It may have a useful class 
# to help you do so. 
#
# If branching will affect the outcome of the check, override and properly
# implement the __eq__ and copy methods. This will allow traverse to handle
# branching for you.
#
# If state is recorded override and properly implement the new_function method.
# This should reset the state of your check when needed by the traverse 
# function.

# An interface for all Checks, which should inherit this class.
class FormalCheckInterface(metaclass=abc.ABCMeta):
	@classmethod
	def __subclasshook__(cls, subclass) -> None:
		return (hasattr(subclass, 'analyse_cursor') and
				callable(subclass.analyse_cursor) or
				NotImplemented)

	def __init__(self) -> None:
		pass

	# All Checks should implement the "analyse_cursor()" method.
	@abc.abstractmethod
	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		raise NotImplementedError

	def __eq__(self, __o: object) -> bool:
		return type(self) == type(__o)
	
	# For branching, the check will be duplicated.
	# If you need
	def copy(self):
		return self
	
	# Informs check if the level of scope has decreased.
	# useful for working with lock_guards and other RAII objects
	def scope_increased(self, alerts):
		pass

	# Informs check if the level of scope has decreased.
	# useful for working with lock_guards and other RAII objects
	def scope_decreased(self, alerts):
		pass

	def new_function(self, alerts):
		pass