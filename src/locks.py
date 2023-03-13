import clang.cindex
from scope import *
from observer import *

import traceback

#TODO some types of locking is not detected
#TODO recursion breaks this
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
#Now handles while loops
#	-Leon Byrne
#
#TODO perhaps give the list of function calls, avoid calling it again
#
# @Param startNode:   the node that analysis is started on, used a bit
# @Param currentNode: the node from which building the thread is done
# @Param scope: 			the current scope which we're in
# @Param eventSource: EventSource to notify observers about currentNode       <- Added by Gráinne Ready
# @Param paths:       a list of booleans dictating how to respond to branching
def build_thread(startFunc, currentNode, scope, eventSource, paths : Paths, calls : Calls):
	if currentNode.kind == clang.cindex.CursorKind.COMPOUND_STMT:
		newScope = Scope(scope.scopeClass)
		scope.add(newScope)
		scope = newScope
	elif currentNode.kind == clang.cindex.CursorKind.CALL_EXPR:
		#eventSource.notifyObservers(currentNode)
		if currentNode.spelling == "lock":
			scope.add(Lock(list(list(currentNode.get_children())[0].get_children())[0].spelling, currentNode.location))
		elif currentNode.spelling == "unlock":
			scope.add(Unlock(list(list(currentNode.get_children())[0].get_children())[0].spelling, currentNode.location))
		elif currentNode.spelling == "lock_guard":
			scope.add(LockGuard(list(currentNode.get_children())[0].spelling, currentNode.location))
		else:
			#Sometimes it's a call expr while not saying it's name
			#It's children will though
			if currentNode.spelling in func and not calls.check_recursion(currentNode):
				newCall = Call(func[currentNode.spelling], currentNode.location)
				scope.add(newCall)
				scope.add(newCall.scope)
				#build_thread(startFunc.node, newCall.function.node, newCall.scope, eventSource)

				calls.add(currentNode)

				build_thread(startFunc, newCall.function.node, newCall.scope, eventSource, paths, calls)

	if currentNode.kind == clang.cindex.CursorKind.IF_STMT:
		if paths.has_next():
			children = list(currentNode.get_children())

			ifScope = Scope(scope.scopeClass)
			scope.add(ifScope)
			build_thread(startFunc, children[0], ifScope, eventSource, paths, calls)

			if paths.get_next():
				build_thread(startFunc, children[1], ifScope, eventSource, paths, calls)
			else:
				if len(children) > 2:
					build_thread(startFunc, children[2], ifScope, eventSource, paths, calls)
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
			build_thread(startFunc, currentNode, scope, eventSource, paths, calls)


			# build_thread(startFunc, startFunc.node, ifScope, eventSource, ifPath)
			build_thread(startFunc, startFunc.node, elseScope, eventSource, elsePath, Calls())	
	elif currentNode.kind == clang.cindex.CursorKind.WHILE_STMT:	
		if paths.has_next():
			children = list(currentNode.get_children())

			firstPass = paths.has_next() and paths.get_next()
			secondPass = firstPass and paths.has_next() and paths.get_next()
			thirdPass = secondPass and paths.has_next() and paths.get_next() #Needed anyways

			whileScope = Scope(scope.scopeClass)
			scope.add(whileScope)
			build_thread(startFunc, children[0], whileScope, eventSource, paths, calls)

			if firstPass:
				build_thread(startFunc, children[1], whileScope, eventSource, paths, calls)

				whileScope = Scope(scope.scopeClass)
				scope.add(whileScope)
				build_thread(startFunc, children[0], whileScope, eventSource, paths, calls)

				if secondPass:
					build_thread(startFunc, children[1], whileScope, eventSource, paths, calls)

					whileScope = Scope(scope.scopeClass)
					scope.add(whileScope)
					build_thread(startFunc, children[0], whileScope, eventSource, paths, calls)
	
				
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

			build_thread(startFunc, currentNode, scope, eventSource, paths, calls)
			build_thread(startFunc, startFunc.node, onceScope, eventSource, oncePath, Calls())
			build_thread(startFunc, startFunc.node, twiceScope, eventSource, twicePath, Calls())

	elif currentNode.kind == clang.cindex.CursorKind.DO_STMT:
		if paths.has_next():

			children = list(currentNode.get_children())
			doScope = Scope(scope.scopeClass)
			scope.add(doScope)

			#In do-while loops the first pass always happens
			secondPass = paths.has_next() and paths.get_next()
			thirdPass = secondPass and paths.has_next() and paths.get_next()

			build_thread(startFunc, children[0], doScope, eventSource, paths, calls)
			build_thread(startFunc, children[1], doScope, eventSource, paths, calls)

			if secondPass:
				doScope = Scope(scope.scopeClass)
				scope.add(doScope)

				build_thread(startFunc, children[0], doScope, eventSource, paths, calls)
				build_thread(startFunc, children[1], scope, eventSource, paths, calls)
		else:			
			
			#No need for a once scope, that is the 'paths.add(False)' one
			twiceScope = Scope(startFunc.functionClass)
			scopes.append(twiceScope)
			twicePath = paths.copy()
			twicePath.add(True)
			twicePath.add(False)

			paths.add(False)

			build_thread(startFunc, currentNode, scope, eventSource, paths, calls)
			build_thread(startFunc, startFunc.node, twiceScope, eventSource, twicePath, Calls())
	
	elif currentNode.kind == clang.cindex.CursorKind.FOR_STMT:
		if paths.has_next():
			children = list(currentNode.get_children())

			firstPass = paths.has_next() and paths.get_next()
			secondPass = firstPass and paths.has_next() and paths.get_next()
			thirdPass = secondPass and paths.has_next() and paths.get_next() #Needed anyways


			forScope = Scope(scope.scopeClass)
			scope.add(forScope)

			build_thread(startFunc, children[0], forScope, eventSource, paths, calls)
			build_thread(startFunc, children[2], forScope, eventSource, paths, calls)

			if firstPass :
				build_thread(startFunc, children[4], forScope, eventSource, paths, calls)

				forScope = Scope(scope.scopeClass)
				scope.add(forScope)
				build_thread(startFunc, children[3], forScope, eventSource, paths, calls)
				build_thread(startFunc, children[2], forScope, eventSource, paths, calls)

				if secondPass :
					build_thread(startFunc, children[4], forScope, eventSource, paths, calls)

					forScope = Scope(scope.scopeClass)
					scope.add(forScope)

					build_thread(startFunc, children[3], forScope, eventSource, paths, calls)
					build_thread(startFunc, children[2], forScope, eventSource, paths, calls)
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

			build_thread(startFunc, currentNode, scope, eventSource, paths, calls)
			build_thread(startFunc, startFunc.node, onceScope, eventSource, oncePath, Calls())
			build_thread(startFunc, startFunc.node, twiceScope, eventSource, twicePath, Calls())
	elif currentNode.kind == clang.cindex.CursorKind.SWITCH_STMT:
		if paths.has_next():
			#Have it go through the list
			children = list(list(currentNode.get_children())[1].get_children())
			
			switchScope = Scope(scope.scopeClass)
			scope.add(switchScope)

			#Pull all switch path booleans
			targetFound = False
			switchBools = Paths()
			while True:
				switchBools.add(paths.get_next())

				if switchBools.paths[-1]:
					targetFound = True
				elif targetFound:
					break

			fallThrough = False
			for child in children:
				if child.kind == clang.cindex.CursorKind.CASE_STMT:
					if fallThrough or switchBools.get_next():
						body = child
						while body.kind == clang.cindex.CursorKind.CASE_STMT:
							body = list(body.get_children())[1]
						build_thread(startFunc, body, switchScope, eventSource, paths, calls)
						fallThrough = True
				elif child.kind == clang.cindex.CursorKind.BREAK_STMT and fallThrough:
					switchBools.get_next()
					return
				elif fallThrough:
					build_thread(startFunc, child, switchScope, eventSource, paths), calls


		elif len(list(currentNode.get_children())) > 1:
			#Count the number of case statements
			#Make new paths for them
			#If there is fall through one path is True until a break and the others
			#start True at different parts
			#
			# EG
			#	case 1:
			# case 2:
			# case 3:
			#		break;
			#
			#	True, True, True
			# False, True, True
			# False, False, True
			#
			#Then start them from the top
			children = list(list(currentNode.get_children())[1].get_children())
			cases = 0

			#Get number of cases
			for child in children:
				if child.kind == clang.cindex.CursorKind.CASE_STMT:
					cases += 1

			#Get list of new scopes and paths
			switchPaths = list()
			switchScopes = list()

			#Fill new lists
			for i in range(0, cases):
				switchPaths.append(paths.copy())
				switchScopes.append(Scope(startFunc.functionClass))
				scopes.append(switchScopes[i])


			for i in range(0, cases):
				for j in range(0, i):
					switchPaths[i].add(False)
				switchPaths[i].add(True)
				switchPaths[i].add(False)


			for i in range(0, len(switchScopes)):
				build_thread(startFunc, startFunc.node, switchScopes[i], eventSource, switchPaths[i], Calls())

			#Only if I search for a defualt
			#build_thread(startFunc, currentNode, scope, eventSource, paths)


		



	else:
		continueBuild = True
		for child in currentNode.get_children():
			if continueBuild:
				returnBuild = build_thread(startFunc, child, scope, eventSource, paths, calls)
				if returnBuild != None:
					continueBuild = returnBuild

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
				warnings.add("Manual locking in file: " + str(a.location.file) + " at line: " + str(a.location.line) + "\n	RAII is preferred")
			if lock_list.lock(a):
				warnings.add("Error: locking locked mutex at:" + str(a.location))
		elif type(a) == Unlock:
			if not manualAllowed:
				warnings.add("Manual unlocking in file: " + str(a.location.file) + " at line: " + str(a.location.line) + "\n	RAII is preferred")
			lock_list.unlock(a)
		elif type(a) == LockGuard:
			if lock_list.lock(a):
				warnings.add("Error at: " + str(a.location))
		elif type(a) == Call:
			if (not callAllowed) and lock_list.order and (a.function.functionClass == None or scope.scopeClass != a.function.functionClass):
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
lock_guard_observer = tagObserver("std::lock_guard<std::mutex>")
eventSource.addObserver(lock_guard_observer)

#Renamed to not interfere with pytest
def run_checks(filename, callAllowed, manualAllowed):
	#I despise How long it took to notice that I needed to clear it between tests
	scopes.clear()
	func.clear()
	order.orders.clear()
	index = clang.cindex.Index.create()
	tu = index.parse(filename)

	get_function(tu.cursor, func, None)

	mainScope = Scope(None)
	scopes.append(mainScope)
	#build_thread(func['main'].node, func['main'].node, mainScope, eventSource)

	build_thread(func['main'], func['main'].node, mainScope, eventSource, Paths(), Calls())

	warningList = WarningList()
	for scope in scopes:
		locks = Locked()
		examine_thread(scope, locks, warningList, callAllowed, manualAllowed)

	# for str in warningList.warnings:
	# 	print(str)

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
	run_checks("../cpp_tests/case_test.cpp", False, True)
