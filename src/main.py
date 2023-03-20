import clang.cindex
import sys, os, importlib.util
from typing import List
from formalCheckInterface import FormalCheckInterface
from alerts import *
from Util import Function
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
	traverse(tu.cursor, check_list, alerts)

	for alert in alerts:
		alert.display()
		print()

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
def traverse(cursor: clang.cindex.Cursor, check_list: List[FormalCheckInterface], alerts):
	# TODO handle switch-case branching
	# TODO handle loops
	# TODO prevent recursion from breaking program
	#      Should be easy, done before -Leon Byrne

	if str(cursor.translation_unit.spelling) == str(cursor.location.file):				
		for check in check_list:
			check.analyse_cursor(cursor, alerts)

		# These that are picked out are special in terms of branching and how it may
		# affect other checks. Eg IF_STMT
		if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL or cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
			for check in check_list:
				check.new_function(cursor, alerts)

			#Only keep unique checks, ie one of each in list
			checkLen = len(check_list)
			for i in range(0, checkLen - 1):
				j = i + 1
				while j < checkLen:
				# for j in range(i + 1, checkLen):
					if check_list[i] == check_list[j]:
						check_list.remove(check_list[j])
						checkLen -= 1
					
					j += 1
			
			for child in cursor.get_children():
				traverse(child, check_list, alerts)

		elif cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT:
			for check in check_list:
				check.scope_increased(alerts)

			for child in cursor.get_children():
				traverse(child, check_list, alerts)
		
			for check in check_list:
				check.scope_decreased(alerts)
		elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
			#First we evaluate the arguements, they may be function calls
			#We can just traverse all the children of the call
			for child in cursor.get_children():
				traverse(child, check_list, alerts)

			if cursor.spelling != "lock" and cursor.spelling != "lock_guard":
				for check in check_list:
					check.analyse_cursor(cursor, alerts)

			#This will skip the FUNCTION_DECL node
			if cursor.referenced is not None:
				traverse(list(cursor.referenced.get_children())[0], check_list, alerts)
		elif cursor.kind == clang.cindex.CursorKind.IF_STMT:
			#traverse condition
			traverse(list(cursor.get_children())[0], check_list, alerts)

			#duplicate checks
			copies = list()
			for check in check_list:
				copies.append(check.copy())

			#traverse if-true body
			traverse(list(cursor.get_children())[1], copies, alerts)

			#needs to be evaluated before for loops and before possible else if tree
			checkLen = len(check_list)

			#traverse if-false body (if present)
			if len(list(cursor.get_children())) > 2:
				traverse(list(cursor.get_children())[2], check_list, alerts)

			for i in range(0, checkLen):
				if copies[i] != check_list[i]:
					check_list.append(copies[i])

			for i in range(checkLen, len(copies)):
				check_list.append(copies[i])
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
						traverse(children[j], copies, alerts)

						if children[j].kind == clang.cindex.CursorKind.BREAK_STMT:
							break

				elif children[i].kind == clang.cindex.CursorKind.DEFAULT_STMT:
					for j in range(i, len(children)):
						traverse(children[j], check_list, alerts)

						if cursor.kind == clang.cindex.CursorKind.BREAK_STMT:
							break

			#TODO Replace indexing used earlier with this
			for copies in copyLists:
				for check in copies:
					if check not in check_list:
						check_list.append(check)

		elif cursor.kind == clang.cindex.CursorKind.WHILE_STMT:
			condition = list(cursor.get_children())[0]
			body = list(cursor.get_children())[1]

			traverse(condition, check_list, alerts)
					
			#duplicate checks
			copies = list()
			for check in check_list:
				copies.append(check.copy())

			traverse(body, copies, alerts)
			traverse(condition, copies, alerts)

			for check in copies:
				if check not in check_list:
					check_list.append(check)

			#duplicate checks
			secondPass = list()
			for check in copies:
				secondPass.append(check.copy())

			traverse(body, secondPass, alerts)
			traverse(condition, secondPass, alerts)

			for check in secondPass:
				if check not in check_list:
					check_list.append(check)

		elif cursor.kind == clang.cindex.CursorKind.DO_STMT:
			body = list(cursor.get_children())[0]
			condition = list(cursor.get_children())[1]

			traverse(body, check_list, alerts)
			traverse(condition, check_list, alerts)

			#duplicate checks
			copies = list()
			for check in check_list:
				copies.append(check.copy())

			traverse(body, copies, alerts)
			traverse(condition, copies, alerts)

			for check in copies:
				if check not in check_list:
					check_list.append(check)

		elif cursor.kind == clang.cindex.CursorKind.FOR_STMT:
			decl = list(cursor.get_children())[0]
			condition = list(cursor.get_children())[1]
			operator = list(cursor.get_children())[2]
			body = list(cursor.get_children())[3]

			traverse(decl, check_list, alerts)
			traverse(condition, check_list, alerts)

			#duplicate checks
			copies = list()
			for check in check_list:
				copies.append(check.copy())

			traverse(body, copies, alerts)
			traverse(operator, copies, alerts)
			traverse(condition, copies, alerts)

			for check in copies:
				if check not in check_list:
					check_list.append(check)		

			#duplicate checks
			secondPass = list()
			for check in copies:
				secondPass.append(check.copy())

			traverse(body, secondPass, alerts)
			traverse(operator, secondPass, alerts)
			traverse(condition, secondPass, alerts)

			for check in secondPass:
				if check not in check_list:
					check_list.append(check)	

		else:
			for child in cursor.get_children():
				traverse(child, check_list, alerts)
	else:
		for child in cursor.get_children():		
			traverse(child, check_list, alerts)			

if __name__ == "__main__":
	main()
