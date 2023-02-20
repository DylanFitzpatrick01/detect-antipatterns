import clang.cindex
from scope import *

#TODO some types of locking is not detected
#TODO recursion breaks this
#TODO no handling is given to re-assignments
#TODO if-else branching is not handled correctly, or at all
#TODO parse through lock orders to detect possible errors
#TODO maybe reduce scope to widest necessary, for easy viewing

#Leon Byrne
#Will return a dictionary of functions keyed by their names (node.spelling)
#Useful for when functions are called by others
#Also does methods
def get_function(node, dict, functionClass):
	if node.kind == clang.cindex.CursorKind.CLASS_DECL:
		for child in node.get_children():
			get_function(child, dict, node.spelling)
	elif node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
		dict[node.spelling] = Function(node, functionClass)
	elif node.kind == clang.cindex.CursorKind.CXX_METHOD:
		dict[node.spelling] = Function(node, functionClass)
	elif node.kind == clang.cindex.CursorKind.CONSTRUCTOR:
		dict[node.spelling] = Function(node, functionClass)
	else:
		for child in node.get_children():
			get_function(child, dict, functionClass)

#Leon Byrne
#Builds a path of execution from one node on
#Will crash if there is recursion within the path
#Will not take into account if-else branchs
# Locking/unlocking in one or the other will be treated as both happening, even
# if impossible to do so
#
#TODO perhaps give the list of function calls, avoid calling it again
#
# @Param node:        the node from which building the thread is done
# @Param scope: 			the current scope which we're in
# @Param callAllowed: whether or not calling out of scope is allowed
def build_thread(node, scope, callAllowed):
	if node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
		newScope = Scope(scope.scopeClass)
		scope.add(newScope)
		scope = newScope

	elif node.kind == clang.cindex.CursorKind.CALL_EXPR:
		if node.spelling == "lock":
			scope.add(Lock(list(list(node.get_children())[0].get_children())[0].spelling, node.location))
		elif node.spelling == "unlock":
			scope.add(Unlock(list(list(node.get_children())[0].get_children())[0].spelling, node.location))
		elif node.spelling == "lock_guard":
			scope.add(LockGuard(list(node.get_children())[0].spelling, node.location))
		else:
			#Sometimes it's a call expr while not saying it's name
			#It's children will though
			if node.spelling in func:
				if callAllowed:
					newScope = Scope()
					scope.add(newScope)
					scope = newScope
					build_thread(func[node.spelling].node, scope, callAllowed)
				else:
					newCall = Call(func[node.spelling], node.location)
					scope.add(newCall)
					scope.add(newCall.scope)
					build_thread(newCall.function.node, newCall.scope, callAllowed)

	for child in node.get_children():
		build_thread(child, scope, callAllowed)

#Leon Byrne
#Runs through a scope and examines it for locks and unlocks
#Will also record the order of locks
def examine_thread(scope, lock_list, str):
	for a in scope.data:
		if type(a) == Scope:
			examine_thread(a, lock_list, str + "  ")
			#When we return from the scope, unlock lockguards
			for b in a.data:
				if type(b) == LockGuard:
					if not lock_list.unlock(b):
						print("Error at: ", b.location)
		elif type(a) == Lock:
			if lock_list.lock(a):
				print("Error at: ", a.location)
		elif type(a) == Unlock:
			lock_list.unlock(a)
		elif type(a) == LockGuard:
			if lock_list.lock(a):
				print("Error at: ", a.location)
		elif type(a) == Call:
			if lock_list.order and (scope.scopeClass != a.function.functionClass or a.function.functionClass == None):
				print(str, "Error: called out of scope: ", a.function.node.spelling,  ", at line", a.location.line)
				
		order.add(lock_list.get_order())

#Leon Byrne
#Creates a neat, printed representation of the scope and locks/unlocks within
def print_scope(scope, str):
	for a in scope.data:
		if type(a) == Scope:
			print(str, "{")
			print_scope(a, str + "  ")
			print(str, "}")
		elif type(a) == Lock:
			print(str, "locking: ", a.mutex)
		elif type(a) == LockGuard:
			print(str, "guarding: ", a.mutex)
		elif type(a) == Unlock:
			print(str, "unlocking: ", a.mutex)


#Leon Byrne
#Maybe remove the global varibales? Not really neat
index = clang.cindex.Index.create()
tu = index.parse("test.cpp")

func = dict()
get_function(tu.cursor, func, None)

print(func['test'].functionClass)

order = LockOrder()

scope = Scope(None)
locks = Locked()
build_thread(func['main'].node, scope, False)
examine_thread(scope, locks, "")

for o in order.orders:
	print("order: ")
	for m in o:
		print(m)