import clang.cindex
import sys, os, importlib.util
from contextlib import redirect_stdout
from typing import List
from formalCheckInterface import FormalCheckInterface
from alerts import *
from Util import Function
from math import floor
# clang.cindex.Config.set_library_file('C:/Program Files/LLVM/bin/libclang.dll')

# Relative directory that contains our check files.
checks_dir = '../Checks'

def main():
	
	# Attempt to get a filename from the command line args.
	# If that fails, ask the user.
	# If both fail, give up.
	s = ""
	try:
		if (len(sys.argv) > 1):
			s = sys.argv[1]
		else:
			s = input("\nEnter the name of the file you'd like to analyse or 'quit' to quit\n > ")
		open(s)
	except FileNotFoundError:
		print("FILE DOES NOT EXIST!\n")
		exit()
		

		# Gets clang to start parsing the file, and generate
		# a translation unit with an Abstract Syntax Tree.
	idx = clang.cindex.Index.create()
	tu = idx.parse(s)

	# Import all of our checks!
	try:
		check_list = list()
		for file in os.listdir(os.path.abspath(os.path.join(os.path.dirname( __file__ ), checks_dir))):
			if (file.endswith(".py") and file != "alerts.py"):
				spec = importlib.util.spec_from_file_location(file.removesuffix(".py"), os.path.abspath(os.path.join(os.path.dirname( __file__ ), checks_dir, file)))
				check_module = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(check_module)
				check_list.append(check_module.Check())
	except FileNotFoundError:
		print(f"checks_dir '{checks_dir}' does not exist! Make sure it's a relative directory to main.py!")
		exit()

	# Traverse the AST
	alerts = list()
	traverse(tu.cursor, check_list, alerts, list())

	# If we're using a regular terminal...
	if sys.stdout.isatty():
		# print to console. Make it look good!
		for alert in alerts:
			alert.display()
	# If we're being piped to a file or FIFO...
	else:
		# Print without colour / unnecessary data.
		for alert in alerts:
			alert.display_unfancy()
				
# --------FUNCTIONS-------- #

# Traverses Clangs cursor tree. A cursor points to a piece of code,
# and has extremely useful values and functions. The cursor tree is
# a generic tree. More info:
# https://libclang.readthedocs.io/en/latest/#clang.cindex.Cursor
# https://www.geeksforgeeks.org/generic-treesn-array-trees/
#
# We run every check on every cursor. The checks can be found at the
# 'checks_dir' above. Each check returns a list of Alerts. This list
# contains everything the check thinks is wrong. This function gathers
# All of those alerts, and returns them.
#
#
# TODO comments
#	TODO be wary of .referenced in regards to functions, it will return the first
#      declaration of it. Eg, void test(); will be returned if test(); node is 
#      .referenced

#	@Param cursor    : The current cursor to traverse/analyse.
#	@Param check_list: The list of checks we will be passing cursor to.
# @Param alerts    : The list of alerts checks will append to.
# @Param calls     : The list of calls made so far, checked for recursion.
def traverse(cursor: clang.cindex.Cursor, check_list: List[FormalCheckInterface], alerts: List[Alert], calls):
	if str(cursor.translation_unit.spelling) == str(cursor.location.file):				
		for check in check_list:
			check.analyse_cursor(cursor, alerts)

		# These that are picked out are special in terms of branching and how it may
		# affect other checks. Eg IF_STMT
		if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL or cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
			#	Some checks only check functions/methods in isolation. new_function can
			# tell them to ditch un-necessary information. Can help both speed and
			# memory usage.
			for check in check_list:
				check.new_function(cursor, alerts)

			#	Removing equal checks
			seenChecks = list()
			for check in check_list:
				if check not in seenChecks:
					seenChecks.append(check)
				else:
					check_list.remove(check)
			
			for child in cursor.get_children():
				traverse(child, check_list, alerts, list())

		elif cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT:
			#	For checks that care about locking mutexes, the calls to scope_increased
			#	and scope_decreased help in managing when lock_guards will leave scope.
			for check in check_list:
				check.scope_increased(alerts)

			for child in cursor.get_children():
				traverse(child, check_list, alerts, calls)
		
			for check in check_list:
				check.scope_decreased(alerts)
		elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			#	Some checks will want to follow possible flows of execution, here we
			# do so and avoid recursion causing a loop in traverse().

			#First we evaluate the arguements, they may be function calls
			#We can just traverse all the children of the call
			for child in cursor.get_children():
				traverse(child, check_list, alerts, calls)

			# Check that it's not in a recursive loop
			# Add next call to list copy
			# Call

			# Don't traverse the FUNCTION_DECL node, just the compound statement after
			if cursor.get_definition() is not None and not check_for_recursion(calls, cursor.referenced.get_usr()):
				# Still want to analyze the funtion/method decl even if we don't want to
				# traverse it
				for check in check_list:
					check.analyse_cursor(cursor.get_definition(), alerts)

				#print(cursor.referenced.get_usr())

				callCopy = calls.copy()
				callCopy.append(cursor.get_definition().get_usr())

				for call in callCopy:
					print(call)

				print()

				for child in cursor.get_definition().get_children():
					traverse(child, check_list, alerts, callCopy)

		elif cursor.kind == clang.cindex.CursorKind.IF_STMT:
			#	For checks which care about if a mutex might be locked at a certain
			#	point, we need to consider that lock/unlocks may happen inside if-elses.

			#traverse condition
			traverse(list(cursor.get_children())[0], check_list, alerts, calls)

			#duplicate checks
			copies = list()
			for check in check_list:
				copies.append(check.copy())

			#traverse if-true body
			traverse(list(cursor.get_children())[1], copies, alerts, calls)

			#traverse if-false body (if present)
			if len(list(cursor.get_children())) > 2:
				traverse(list(cursor.get_children())[2], check_list, alerts, calls)

			#	Save unique checks
			for check in copies:
				if check not in check_list:
					check_list.append(check)
		elif cursor.kind == clang.cindex.CursorKind.SWITCH_STMT:
			children = list(list(cursor.get_children())[1].get_children())
			copyLists = list()

			for i in range(0, len(children)):
				if children[i].kind == clang.cindex.CursorKind.CASE_STMT:
					#duplicate checks
					copies = list()
					for check in check_list:
						copies.append(check.copy())

					copyLists.append(copies)

					for j in range(i, len(children)):
						traverse(children[j], copies, alerts, calls)

						if children[j].kind == clang.cindex.CursorKind.BREAK_STMT:
							break

				elif children[i].kind == clang.cindex.CursorKind.DEFAULT_STMT:
					for j in range(i, len(children)):
						traverse(children[j], check_list, alerts, calls)

						if cursor.kind == clang.cindex.CursorKind.BREAK_STMT:
							break

			for copies in copyLists:
				for check in copies:
					if check not in check_list:
						check_list.append(check)

		elif cursor.kind == clang.cindex.CursorKind.WHILE_STMT:
			condition = list(cursor.get_children())[0]
			body = list(cursor.get_children())[1]

			traverse(condition, check_list, alerts, calls)
					
			#duplicate checks
			copies = list()
			for check in check_list:
				copies.append(check.copy())

			traverse(body, copies, alerts, calls)
			traverse(condition, copies, alerts, calls)

			for check in copies:
				if check not in check_list:
					check_list.append(check)

			#duplicate checks
			secondPass = list()
			for check in copies:
				secondPass.append(check.copy())

			traverse(body, secondPass, alerts, calls)
			traverse(condition, secondPass, alerts, calls)

			for check in secondPass:
				if check not in check_list:
					check_list.append(check)

		elif cursor.kind == clang.cindex.CursorKind.DO_STMT:
			body = list(cursor.get_children())[0]
			condition = list(cursor.get_children())[1]

			traverse(body, check_list, alerts, calls)
			traverse(condition, check_list, alerts, calls)

			#duplicate checks
			copies = list()
			for check in check_list:
				copies.append(check.copy())

			traverse(body, copies, alerts, calls)
			traverse(condition, copies, alerts, calls)

			for check in copies:
				if check not in check_list:
					check_list.append(check)

		elif cursor.kind == clang.cindex.CursorKind.FOR_STMT:
			decl = list(cursor.get_children())[0]
			condition = list(cursor.get_children())[1]
			operator = list(cursor.get_children())[2]
			body = list(cursor.get_children())[3]

			traverse(decl, check_list, alerts, calls)
			traverse(condition, check_list, alerts, calls)

			#duplicate checks
			copies = list()
			for check in check_list:
				copies.append(check.copy())

			traverse(body, copies, alerts, calls)
			traverse(operator, copies, alerts, calls)
			traverse(condition, copies, alerts, calls)

			for check in copies:
				if check not in check_list:
					check_list.append(check)		

			#duplicate checks
			secondPass = list()
			for check in copies:
				secondPass.append(check.copy())

			traverse(body, secondPass, alerts, calls)
			traverse(operator, secondPass, alerts, calls)
			traverse(condition, secondPass, alerts, calls)

			for check in secondPass:
				if check not in check_list:
					check_list.append(check)	

		else:
			for child in cursor.get_children():
				traverse(child, check_list, alerts, calls)
	else:
		for child in cursor.get_children():		
			traverse(child, check_list, alerts, calls)			

#	This function will check if a given list of function call USRs (universal
# symbol representations) contains a case of recursion.
#
#	Eg: a->b->c->d->c->d, calling c->d after c->d is recursion and we will return
#	true is the nextCall is c
def check_for_recursion(calls, nextCall) -> bool:
	for i in range(1, floor(len(calls) / 2) + 1):
		# i is the number of calls we're checking at once

		recursive = True
		if calls[-i] != nextCall:
			recursive = False

		for j in range(1, i + 1):
			if calls[-j] != calls[-(j + i)]:
				recursive = False

		if recursive:
			return True
	return False

if __name__ == "__main__":
	main()
