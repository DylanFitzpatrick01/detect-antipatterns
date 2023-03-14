import clang.cindex
import sys, os, importlib.util
from typing import List
from formalCheckInterface import FormalCheckInterface
from alerts import Alert
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
	tu = idx.parse(s, args=['-std=c++11'])

	# Import all of our checks!
	try:
		check_list = list()
		for file in os.listdir(os.path.abspath(os.path.join(os.path.dirname( __file__ ), checks_dir))):
			if (file.endswith("calledOutOfLockedScope.py") and file != "alerts.py"):
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
	if cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT:
		for check in check_list:
			check.scope_increased()

		for child in cursor.get_children():
			traverse(child, check_list, alerts)
		
		for check in check_list:
			check.scope_decreased()
	else:
		# if(str(cursor.translation_unit.spelling) == str(child_cursor.location.file)):
		# 	for check in check_list:
		# 		check.analyse_cursor(cursor, alerts)
		
		for child in cursor.get_children():
			if(str(cursor.translation_unit.spelling) == str(child.location.file)):
				for check in check_list:
					check.analyse_cursor(cursor, alerts)
			traverse(child, check_list, alerts)

	# alerts: List[Alert] = list()

	# # For every cursor in the AST...
	# child_cursor: clang.cindex.Cursor
	# for child_cursor in cursor.walk_preorder():

	#     # This line makes sure that the line of code our cursor points to
	#     # is in the same file that our translation unit is analysing.
	#     #
	#     # This means no cursors from header files! If this wasn't here,
	#     # we'd be looking at the cursors of HUNDREDS of microsoft C++ 
	#     # std functions.
	#     #
	#     if(str(cursor.translation_unit.spelling) == str(child_cursor.location.file)):

	#         # -------DETECTION LOGIC HERE!-------
	#         # Runs all of our checks, on every cursor in the tree.
	#         # Adds the alerts they raise to the alerts pile!
	#         for check in check_list:
	#             alerts.extend(check.analyse_cursor(child_cursor))
	
	# # Complain!
	# return alerts
			

if __name__ == "__main__":
	main()
