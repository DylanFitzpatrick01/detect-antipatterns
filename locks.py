import clang.cindex
from scope import *
from observer import *

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
#Now acounts for branching
# -Leon Byrne
#
#TODO perhaps give the list of function calls, avoid calling it again
#
# @Param startNode:   the node that analysis is started on, used a bit
# @Param currentNode:        the node from which building the thread is done
# @Param scope: 			the current scope which we're in
# @Param eventSource:       EventSource to notify observers about currentNode       <- Added by Gráinne Ready
# def build_thread(startNode, currentNode, scope, eventSource):
# 	if currentNode.kind == clang.cindex.CursorKind.COMPOUND_STMT:
# 		newScope = Scope(scope.scopeClass)
# 		scope.add(newScope)
# 		scope = newScope
# 	elif currentNode.kind == clang.cindex.CursorKind.CALL_EXPR:
# 		eventSource.notifyObservers(currentNode)
# 		if currentNode.spelling == "lock":
# 			scope.add(Lock(list(list(currentNode.get_children())[0].get_children())[0].spelling, currentNode.location))
# 		elif currentNode.spelling == "unlock":
# 			scope.add(Unlock(list(list(currentNode.get_children())[0].get_children())[0].spelling, currentNode.location))
# 		elif currentNode.spelling == "lock_guard":
# 			scope.add(LockGuard(list(currentNode.get_children())[0].spelling, currentNode.location))
# 		else:
# 			#Sometimes it's a call expr while not saying it's name
# 			#It's children will though
# 			if currentNode.spelling in func:
# 				newCall = Call(func[currentNode.spelling], currentNode.location)
# 				scope.add(newCall)
# 				scope.add(newCall.scope)
# 				build_thread(startNode, newCall.function.node, newCall.scope, eventSource)

# 	if currentNode.kind == clang.cindex.CursorKind.IF_STMT:
# 		children = list(currentNode.get_children())

# 		#Build the first child as evalutation could have locking/unlocking in it
# 		ifScope = Scope(scope.scopeClass)
# 		scope.add(ifScope)
# 		build_thread(startNode, children[0], ifScope, eventSource)

# 		#Build inside of if statement
# 		scopeCopy = ifScope.copy()
# 		build_else_thread(startNode, startNode, children[1], scopeCopy.get_scope_root(), True)
# 		scopes.append(scopeCopy.get_scope_root())

# 		#only if has else statement
# 		if len(children) >= 3:
# 			build_else_thread(startNode, startNode, children[2], ifScope.get_scope_root(), True)
# 	elif currentNode.kind == clang.cindex.CursorKind.WHILE_STMT:
# 		#Doesn't work right -Leon Byrne

# 		children = list(currentNode.get_children())

# 		#Build condition check -No run
# 		whileScope = Scope(scope.scopeClass)
# 		scope.add(whileScope)
# 		build_thread(startNode, children[0], whileScope, eventSource)

# 		#Build body -One run
# 		whileScopeOne = whileScope.copy()
# 		scopes.append(whileScopeOne.get_scope_root())
# 		build_thread(startNode, children[1], whileScopeOne, eventSource)

# 		#Build condition check -One run
# 		whileScopeTwo = Scope(scope.scopeClass)
# 		whileScopeOne.parent.add(whileScopeTwo)
# 		build_thread(startNode, children[0], whileScopeTwo, eventSource)

# 		#Build body -Two runs
# 		whileScopeTwo = whileScopeTwo.copy()
# 		scopes.append(whileScopeTwo.get_scope_root())
# 		build_thread(startNode, children[1], whileScopeTwo, eventSource)

# 		#Build condition check -Two runs
# 		whileScopeThree = Scope(scope.scopeClass)
# 		whileScopeTwo.parent.add(whileScopeThree)
# 		build_thread(startNode, children[0], whileScopeThree, eventSource)

# 		#Build all else for one run
# 		#build_else_thread(startNode, startNode, children[1], whileScopeTwo.get_scope_root(), False)
# 		#build_else_thread(startNode, startNode, children[1], whileScopeThree.get_scope_root(), False)
# 	else:
# 		#Don't build if-node children. The above is required to handle that
# 		for child in currentNode.get_children():
# 			build_thread(startNode, child, scope, eventSource)

#
def build_thread(startFunc, currentNode, scope, eventSource, paths : Paths):
	if currentNode.kind == clang.cindex.CursorKind.COMPOUND_STMT:
		newScope = Scope(scope.scopeClass)
		scope.add(newScope)
		scope = newScope
	elif currentNode.kind == clang.cindex.CursorKind.CALL_EXPR:
		#eventSource.notifyObservers(currentNode)
		if currentNode.spelling == "lock":
			if len(list(currentNode.get_children())) <= 0:
				print(currentNode.location)
				print("huh")
				temp = list(list(currentNode.get_children())[0].get_children())
				print("HUH?")
			scope.add(Lock(list(list(currentNode.get_children())[0].get_children())[0].spelling, currentNode.location))
		elif currentNode.spelling == "unlock":
			scope.add(Unlock(list(list(currentNode.get_children())[0].get_children())[0].spelling, currentNode.location))
		elif currentNode.spelling == "lock_guard":
			scope.add(LockGuard(list(currentNode.get_children())[0].spelling, currentNode.location))
		else:
			#Sometimes it's a call expr while not saying it's name
			#It's children will though
			if currentNode.spelling in func:
				newCall = Call(func[currentNode.spelling], currentNode.location)
				scope.add(newCall)
				scope.add(newCall.scope)
				#build_thread(startFunc.node, newCall.function.node, newCall.scope, eventSource)

				build_thread(startFunc, newCall.function.node, newCall.scope, eventSource, paths)

	if currentNode.kind == clang.cindex.CursorKind.IF_STMT:
		if paths.has_next():
			children = list(currentNode.get_children())

			ifScope = Scope(scope.scopeClass)
			scope.add(ifScope)
			build_thread(startFunc, children[0], ifScope, eventSource, paths)

			if paths.get_next():
				build_thread(startFunc, children[1], ifScope, eventSource, paths)
			else:
				if len(children) > 2:
					build_thread(startFunc, children[2], ifScope, eventSource, paths)
		else:
			# ifPath = paths.copy()
			# ifPath.add(True)
			# ifScope = Scope(startFunc.functionClass)
			# scopes.append(ifScope)


			elsePath = paths.copy()
			elsePath.add(False)
			elseScope = Scope(startFunc.functionClass)
			scopes.append(elseScope)

			paths.add(True)
			build_thread(startFunc, currentNode, scope, eventSource, paths)


			# build_thread(startFunc, startFunc.node, ifScope, eventSource, ifPath)
			build_thread(startFunc, startFunc.node, elseScope, eventSource, elsePath)	
	elif currentNode.kind == clang.cindex.CursorKind.WHILE_STMT:	
		if paths.has_next():
			children = list(currentNode.get_children())

			whileScope = Scope(scope.scopeClass)
			scope.add(whileScope)
			build_thread(startFunc, children[0], whileScope, eventSource, paths)

			firstPass = paths.has_next() and paths.get_next()
			secondPass = firstPass and paths.has_next() and paths.get_next()
			thirdPass = secondPass and paths.has_next() and paths.get_next()

			if firstPass:
				build_thread(startFunc, children[1], whileScope, eventSource, paths)

				whileScope = Scope(scope.scopeClass)
				scope.add(whileScope)
				build_thread(startFunc, children[0], whileScope, eventSource, paths)

				if secondPass:
					build_thread(startFunc, children[1], whileScope, eventSource, paths)

					whileScope = Scope(scope.scopeClass)
					scope.add(whileScope)
					build_thread(startFunc, children[0], whileScope, eventSource, paths)

				
		else:
			#build false
			#build true, false
			#build true, true, false
			children = list(currentNode.get_children())

			onceScope = Scope(startFunc.functionClass)
			scopes.append(onceScope)
			oncePath = paths.copy()
			oncePath.add(True)
			oncePath.add(False)

			twiceScope = Scope(startFunc.functionClass)
			scopes.append(twiceScope)
			twicePath = paths.copy()
			twicePath.add(True)
			twicePath.add(True)
			twicePath.add(False)

			paths.add(False)

			build_thread(startFunc, currentNode, scope, eventSource, paths)
			build_thread(startFunc, startFunc.node, onceScope, eventSource, oncePath)
			build_thread(startFunc, startFunc.node, twiceScope, eventSource, twicePath)

	else:
		for child in currentNode.get_children():
			build_thread(startFunc, child, scope, eventSource, paths)
			


#When an else is detected this method will build it.
#Has to restart building and only starts building once elseNode is found.
#Ignores nodes beforehand.
#Assumes that scope is 'pre-built' up to the elseNode if include else is true
#
#-Leon Byrne
#
#TODO test if this works right if branching outside of main
#			It does not
#			It also does not catch all possible branches
#			If outside of a function, it won't find else even if in path of exection
def build_else_thread(startNode, currentNode, elseNode, scope, includeElse: bool):
	children = list(currentNode.get_children())
	build = False

	for i in range(len(children)):
		if build:
			build_thread(startNode, children[i], scope, eventSource)
		elif children[i] == elseNode:
			build = False
			if includeElse:
				build_thread(startNode, children[i], scope, eventSource)
			return False
		elif node_contains(children[i], elseNode, func):	
			if children[i].kind == clang.cindex.CursorKind.COMPOUND_STMT:
				build = build_else_thread(startNode, children[i], elseNode, scope.data[-1], includeElse)
			elif children[i].kind == clang.cindex.CursorKind.WHILE_STMT:
				build = build_else_thread(startNode, children[i], elseNode, scope.data[-1], includeElse)
			else:
				build = build_else_thread(startNode, children[i], elseNode, scope, includeElse)

		if children[i].kind == clang.cindex.CursorKind.CALL_EXPR and children[i].spelling in func:
			build = build_else_thread(startNode, func[children[i].spelling].node, elseNode, scope.data[-1], includeElse)
	

			
	return build or currentNode.kind == clang.cindex.CursorKind.IF_STMT

#Leon Byrne
#Runs through a scope and examines it for locks and unlocks
#Will also record the order of locks
def examine_thread(scope, lock_list, warnings, callAllowed, manualAllowed):
	for a in scope.data:
		if type(a) == Scope:
			examine_thread(a, lock_list, warnings, callAllowed, manualAllowed)
			#When we return from the scope, unlock lockguards
			for b in a.data:
				if type(b) == LockGuard:
					if not lock_list.unlock(b):
						warnings.add("Error at: " + b.location)
		elif type(a) == Lock:
			if not manualAllowed:
				warnings.add("Manual locking in file: " + str(a.location.file) + " at line: " + str(a.location.line) + "\n  RAII is preferred")
			if lock_list.lock(a):
				warnings.add("Error: locking locked mutex at:" + str(a.location))
		elif type(a) == Unlock:
			if not manualAllowed:
				warnings.add("Manual unlocking in file: " + str(a.location.file) + " at line: " + str(a.location.line) + "\n  RAII is preferred")
			lock_list.unlock(a)
		elif type(a) == LockGuard:
			if lock_list.lock(a):
				warnings.add("Error at: " + str(a.location))
		elif type(a) == Call:
			if (not callAllowed) and lock_list.order and (scope.scopeClass != a.function.functionClass or a.function.functionClass == None):
				warnings.add("Called: " + a.function.node.spelling + " from a locked scope in file: " + str(a.location.file) + " at line: " + str(a.location.line))
				
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


#Liam Byrne
#Checks order in which locks are aquired and releases them in the correct order. 
#Prints error if mutex is already held
def check_lock_order(order):
		held_locks = set()
		for mutex in order:
				if mutex in held_locks:
						print("Error: mutex", mutex, "is already held")
				else:
						held_locks.add(mutex)
		for mutex in reversed(order):
				held_locks.remove(mutex)


#Leon Byrne
#Maybe remove the global variables? Not really neat


func = dict()

order = LockOrder()

#Contains all built scopes
scopes = list()

# Grainne Ready
# 
eventSource = EventSource()
lock_guard_observer = concreteObserver("std::lock_guard<std::mutex>")
eventSource.addObserver(lock_guard_observer)


def tests(filename, callAllowed, manualAllowed):
	index = clang.cindex.Index.create()
	tu = index.parse(filename)

	get_function(tu.cursor, func, None)

	mainScope = Scope(None)
	scopes.append(mainScope)
	#build_thread(func['main'].node, func['main'].node, mainScope, eventSource)

	build_thread(func['main'], func['main'].node, mainScope, eventSource, Paths())

	warningList = WarningList()
	for scope in scopes:
		locks = Locked()
		examine_thread(scope, locks, warningList, callAllowed, manualAllowed)

	for str in warningList.warnings:
		print(str)

	#might leve in as is useful to show that we catalogue the orders
	# for o in order.orders:
	# 	print("order: ")
	# 	for m in o:
	# 		print(m)
		#check_lock_order(o)

	#Useful for debugging.
	#Not really a demo-able thing though
	#
	# for a in scopes:
	# 	print("Start")
	# 	print_scope(a, "")

	return warningList.warnings

if __name__ == "__main__":
	tests("cpp_tests/calling_out_of_locked_scope_1.cpp", False, True)