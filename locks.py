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
#Now acounts for branching
# -Leon Byrne
#
#TODO perhaps give the list of function calls, avoid calling it again
#
# @Param startNode:   the node that analysis is started on, used a bit
# @Param currentNode:        the node from which building the thread is done
# @Param scope: 			the current scope which we're in
# @Param callAllowed: whether or not calling out of scope is allowed
def build_thread(startNode, currentNode, scope, callAllowed):
	if currentNode.kind == clang.cindex.CursorKind.COMPOUND_STMT:
		newScope = Scope(scope.scopeClass)
		scope.add(newScope)
		scope = newScope
	elif currentNode.kind == clang.cindex.CursorKind.CALL_EXPR:
		if currentNode.spelling == "lock":
			scope.add(Lock(list(list(currentNode.get_children())[0].get_children())[0].spelling, currentNode.location))
		elif currentNode.spelling == "unlock":
			scope.add(Unlock(list(list(currentNode.get_children())[0].get_children())[0].spelling, currentNode.location))
		elif currentNode.spelling == "lock_guard":
			scope.add(LockGuard(list(currentNode.get_children())[0].spelling, currentNode.location))
		else:
			#Sometimes it's a call expr while not saying it's name
			#It's children will though
			if currentNode.spelling in func:
				if callAllowed:
					newScope = Scope()
					scope.add(newScope)
					scope = newScope
					build_thread(startNode, func[currentNode.spelling].node, scope, callAllowed)
				else:
					newCall = Call(func[currentNode.spelling], currentNode.location)
					scope.add(newCall)
					scope.add(newCall.scope)
					build_thread(startNode, newCall.function.node, newCall.scope, callAllowed)


	if currentNode.kind == clang.cindex.CursorKind.IF_STMT:
		children = list(currentNode.get_children())
		build_thread(startNode, children[0], scope, callAllowed)

		#only if has else statement
		if len(children) >= 3:
			print("else:", children[2].location)
			scopeCopy = scope.copy()
			elseScope = Scope(scopeCopy.scopeClass)
			scopeCopy.add(elseScope)
			build_else_thread(startNode, startNode, children[2], elseScope, callAllowed)
			scopes.append(elseScope.get_scope_root())

		build_thread(startNode, children[1], scope, callAllowed)
	else:
		#Don't build if-node children. The above is required to handle that
		for child in currentNode.get_children():
			build_thread(startNode, child, scope, callAllowed)

#When an else is detected this method will build it.
#Has to restart building and only starts building once elseNode is found.
#Ignores nodes beforehand.
#Assumes that scope is 'pre-built' up to the elseNode
#
#-Leon Byrne
def build_else_thread(startNode, currentNode, elseNode, scope, callAllowed):
	children = list(currentNode.get_children())
	build = False

	for i in range(len(children)):
		if build:
			build_thread(startNode, children[i], scope, callAllowed)
		elif children[i] == elseNode:
			build = True
			build_thread(startNode, children[i], scope, callAllowed)
		elif node_contains(children[i], elseNode):
			build_else_thread(startNode, children[i], elseNode, scope, callAllowed)
			build = True
		elif children[i].kind == clang.cindex.CursorKind.CALL_EXPR:
			build_else_thread(startNode, func[children[i].spelling].node, elseNode, scope, callAllowed)
		


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

order = LockOrder()

#Contains all built scopes
scopes = list()

mainScope = Scope(None)
scopes.append(mainScope)
build_thread(func['main'].node, func['main'].node, mainScope, False)

for scope in scopes:
	locks = Locked()
	examine_thread(scope, locks, "")

for o in order.orders:
	print("order: ")
	for m in o:
		print(m)

for a in scopes:
	print("Start")
	print_scope(a, "")