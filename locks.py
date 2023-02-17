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
def get_function(node, dict):
  if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
    dict[node.spelling] = node
  elif node.kind == clang.cindex.CursorKind.CXX_METHOD:
    dict[node.spelling] = node
  elif node.kind == clang.cindex.CursorKind.CONSTRUCTOR:
    dict[node.spelling] = node
  else:
    for child in node.get_children():
      get_function(child, dict)

#Leon Byrne
#Builds a path of execution from one node on
#Will crash if there is recursion within the path
#Will not take into account if-else branchs
# Locking/unlocking in one or the other will be treated as both happening, even
# if impossible to do so
def build_thread(node, scope):
  if node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
    newScope = Scope()
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
        newScope = Scope()
        scope.add(newScope)
        scope = newScope
        build_thread(func[node.spelling], scope)

  for child in node.get_children():
    build_thread(child, scope)

#Leon Byrne
#Runs through a scope and examines it for locks and unlocks
#Will also record the order of locks
def examine_thread(scope, lock_list):
  for a in scope.data:
    if type(a) == Scope:
      examine_thread(a, lock_list)
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
get_function(tu.cursor, func)

order = LockOrder()

scope = Scope()
locks = Locked()
build_thread(func['main'], scope)
examine_thread(scope, locks)

print_scope(scope, "")

for o in order.orders:
  print("order: ")
  for m in o:
    print(m)