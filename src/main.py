import clang.cindex
import sys, os, importlib, argparse, inspect
from typing import List
from formalCheckInterface import FormalCheckInterface
from alerts import *
from Util import Function
from math import floor
from alerts import Alert
from colour import term_colour

def main():
    # Get our argmuents namespace from the user.
    args = init_argparse()

    # Import all of our checks!
    check_list: List[FormalCheckInterface] = import_checks(args.checks_dir)
    
    # Things to keep track of as we analyse files.
    alerts: List[Alert] = list()
    diagnostics: List[clang.cindex.Diagnostic] = list()

    # Run every check on every cursor of every file.
    for index, file in enumerate(args.locations):
        # Progress bar for terminals.
        progress_bar(index,len(args.locations),40,suffix=' of files analysed')

        # Generate the file's translation unit / Abstract Syntax Tree.
        idx = clang.cindex.Index.create()
        tu = idx.parse(file)

        # If anything went wrong with the translation unit, let us know.        
        diagnostics.extend([diag for diag in tu.diagnostics])

        # Traverse the AST, run each check on every node,
        # and collect any alerts raised by each check.
        alerts.extend(traverse(tu.cursor, check_list))

    # Complete the progress bar.
    progress_bar(1,1,40,suffix=' of files analysed')

    # Print out Clang diagnostics if asked.
    display_diagnostics(diagnostics, args.clang_diags,
                        args.verbose, args.ignore_list)

    # print to console, with as much info as requested.
    for alert in alerts:
        if (alert.severity not in args.ignore_list):
            alert.display(args.verbose)




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
      # And only if it's in the same file.
			if cursor.get_definition() is not None and str(cursor.get_definition().translation_unit.spelling) == str(cursor.get_definition().location.file) and not check_for_recursion(calls, cursor.referenced.get_usr()):
				# Still want to analyze the funtion/method decl even if we don't want to
				# traverse it
				for check in check_list:
					check.analyse_cursor(cursor.get_definition(), alerts)

				callCopy = calls.copy()
				callCopy.append(cursor.get_definition().get_usr())

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

			#traverse else body (if present)
			if len(list(cursor.get_children())) > 2:
				traverse(list(cursor.get_children())[2], check_list, alerts, calls)

			#	Save unique checks
			for check in copies:
				if check not in check_list:
					check_list.append(check)
		elif cursor.kind == clang.cindex.CursorKind.SWITCH_STMT:
			#	Getting a list of all the cases, case bodies, breaks, etc
			children = list(list(cursor.get_children())[1].get_children())
			copyLists = list()

			for i in range(0, len(children)):
				if children[i].kind == clang.cindex.CursorKind.CASE_STMT:
					#duplicate checks
					copies = list()
					for check in check_list:
						copies.append(check.copy())

					copyLists.append(copies)

					#	Due to fall-through we will traverse all cases after until break is
					#	reached.
					for j in range(i, len(children)):
						traverse(children[j], copies, alerts, calls)

						if children[j].kind == clang.cindex.CursorKind.BREAK_STMT:
							break

				#	We pass the regular check_list in default same way as we due for else.
				#	Default states that the program must choose one case from the switch 
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
			#	We check loops like this as some checks may check for changes that occur
			# and may cause deadlocks on a second run.

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

			#	We must run the body at least once, so check_list is passed first
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
			#	If cursor is not a special kind we just traverse it's children
			for child in cursor.get_children():
				traverse(child, check_list, alerts, calls)
	else:
		#	If cursor is not in the file we traverse it's children
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
    # Start at one, then work up to half of all existing calls

    # Assume true, look for contradiction
		recursive = True
		
    # It can't be recursive if the start of one group isn't the nextCall
		if calls[-i] != nextCall:
			recursive = False

    # If two calls in similar places in their respective groups are different
    # then it's not recursive
		for j in range(1, i + 1):
			if calls[-j] != calls[-(j + i)]:
				recursive = False

		if recursive:
			return True
	return False

# Returns an argument parser initialised with the users arguments.
# Automatically rejects nonexistent files/directories and unsupported file types.
def init_argparse() -> argparse.ArgumentParser:

    global checks_dir

    # Setting up the argument parser.
    parser = argparse.ArgumentParser(
        description='Detects common C++ concurrency anti-patterns and malpractices pre-compile.',
        epilog='The default ouput is designed for log files; to be picked up by another program, NOT '
               'TO BE READ BY REAL PEOPLE. Verbosity  (-v) is recommended for humans.'
    )
    parser.add_argument('checks_dir',
                        type=    str,
                        help=    'The directory containing the check programs. These are .py files '
                                 'with a single search pattern. These programs can be moved, deleted '
                                 'and edited. The program will run all checks it finds in this directory.')
    parser.add_argument('locations',
                        nargs=   '*',
                        type=    str,
                        help=    'The files/directories to analyse. '
                                 'Supports multiple locations separated by commas and/or whitespace. '
                                 'If no value is given, data is read from stdin, '
                                 'prompting the user if nessessary.')
    parser.add_argument('-v', '--verbose',
                        action=  'count',
                        default= 0,
                        help=    'increases output verbosity level by one')
    parser.add_argument('-d', '--clang_diags',
                        action=  "store_true",
                        help=    'print out Clang parser diagnostics, helpful if your files aren\'t '
                                 'parsing correctly. Doesn\'t display header/footer text when piped')
    parser.add_argument('-i', '--ignore_list',
                        nargs=   '*',
                        default= [],
                        help=    'types of alert to ignore (i.e. warning, error)')
    parser.add_argument('-l', '--libclang_dir',
                        type=    str,
                        default= [],
                        help=    'manually point to the location of libclang(.so|.dll|.dylib)')
    parser.add_argument('-c', '--clang_args',
                        help=    'manually pass command line arguments to the Clang compiler.'
                                 'takes in a single string containing all commands, space separated. '
                                 'For example, if you want to add a directory to Clang\'s include-'
                                 'path: [prev_args] --clang_args "-I DIRECTORY_TO_INCLUDE"')
    
    args = parser.parse_args()

    # If we have a libclang location, set it!
    if libdir := args.libclang_dir:
        if   os.path.isdir(libdir):  clang.cindex.Config.set_library_path(libdir)
        elif os.path.isfile(libdir): clang.cindex.Config.set_library_file(libdir)
    
    # Turn our string of Clang args into a list.
    if cargs := args.clang_args:
        setattr(args, "clang_args", cargs.split())

    # Absolute-ify our checks directory.
    setattr(args, "checks_dir", os.path.abspath(args.checks_dir))

    # If we don't have any locations, read from stdin:
    # If we're reading stdin from a terminal, print some helpful text, then read from stdin.
    if args.locations == [] and os.isatty(sys.stdin.fileno()):
        args.locations.extend(input("\nEnter the name of the file(s) you'd like to analyse, "
                               "or type '-h' for help:\n > ").replace(',',' ').split())
        if (args.locations[0] == "-h" or args.locations[0].lower() == "--help"):
            raise SystemExit(parser.print_help())

    # If we're not reading stdin from the terminal, just read sys.stdin.
    elif args.locations == [] and os.isatty(sys.stdin.fileno()):
        args.locations.extend(sys.stdin.read().replace(',',' ').split())
    
    # Check all of the locations we recieved.
    for index, loc in enumerate(args.locations):

        # If the location is a directory, replace that directory with all of the .cpp files in it.
        if os.path.isdir(loc):
            del args.locations[index]
            args.locations.extend(list(set().union(
                args.locations, [os.path.join(loc,x) for x in os.listdir(loc) if x.endswith('.cpp')])))
        
        # Make sure the location and checks_dir actually exist, and our locations our .cpp files.
        if not (os.path.isfile(loc) or os.path.isdir(loc)):
            raise parser.error(f"file/directory does not exist: '{loc}'")
        elif os.path.isfile(loc) and not loc.endswith('.cpp'):
            raise parser.error(f"unsupported file type: '{loc}'")
        if not os.path.isdir(args.checks_dir):
            raise parser.error(f"checks directory does not exist: '{args.checks_dir}'")
    
    # Make sure all locations are an absolute path before we return.
    args.locations = list([os.path.abspath(x) for x in args.locations])
    return args


# Given a checks directory, return a list of check objects.
def import_checks(checks_directory: str) -> List[FormalCheckInterface]:
    check_list = list()

    # For all of the python files in the checks directory...
    for file in [x for x in os.listdir(checks_directory) if x.endswith('.py')]:

        # Get the associated python module...
        sys.path.append(str(checks_directory))
        check_module = importlib.import_module(file.removesuffix('.py'))

        # Look at all of the classes in that module...
        for name_local in dir(check_module):
            check_class = getattr(check_module, name_local)

            # If it inherits from our check interface, then append an
            # object of it to our check list!
            if (inspect.isclass(check_class) and issubclass(check_class,FormalCheckInterface)):
                check_list.append(check_class())
    
    return check_list


# Given a list of diagnostics, a show_diags flag, a verbosity count,
# and an ignore list, display all relevant data.
def display_diagnostics(diag_list: List[clang.cindex.Diagnostic],
                        show_diags: bool = True,
                        verbose: int = 0,
                        ignore_list: List[str] = []):
    
    # If we want to show diagnostics, or are being verbose, print diags.
    if (show_diags or verbose > 1):
        # Only print header/footer if we're outputting to a terminal.
        if (sys.stdout.isatty()):
            print(f"\n### Clang parser diagnostics ###\n"f"{len(diag_list)} diagnostics found - ")
            term_colour("red")
            print(f"{len([diag for diag in diag_list if diag.severity==clang.cindex.Diagnostic.Fatal])} fatal, ")
            term_colour("light red")
            print(f"{len([diag for diag in diag_list if diag.severity==clang.cindex.Diagnostic.Error])} errors, ")
            term_colour("yellow")
            print(f"{len([diag for diag in diag_list if diag.severity==clang.cindex.Diagnostic.Warning])} warnings.\n")
            term_colour("native")
        for diagnostic in diag_list:
            print(("\t" if sys.stdout.isatty() else "") + f"{diagnostic}")
        if (sys.stdout.isatty() and len(diag_list) > 0):
            print("\nIf you're having problems parsing, try looking up these Clang diagnostics.\n"
                  "If you find the right Clang command/argument to fix the problem, you can\n"
                  "pass arguments directly to Clang with --clang_args (see --help for more)\n")

    # If we have diagnostics to show, but the user hasn't asked for
    # diagnostics and aren't suppressing warnings, let the user know.
    elif (len(diag_list) > 0 and "warning" not in ignore_list):
        term_colour("yellow")
        print("WARNING: ")
        term_colour("native")
        print(f"{len(diag_list)} compiler alerts raised. (--clang_diags for more information)")


# Progress bar!
def progress_bar(amount:float,max:float,length:int,prefix='',suffix:str=''):
    if sys.stdout.isatty():                 # If we're outputting to a terminal...
        percent = (amount*100)/max          # Get our percentage
        pc_str = '{:.1f}%'.format(percent)  # Make a formatted percentage string
        length_div = 100/(length-8)         # Get the right divisor so that we achieve our desired length.

        term_colour("native")               # The prefix, and start of the bounding box. 
        print(f"[\b \r{prefix}[", end='')

        term_colour("light green")          # The start of the bar.
        print(f"{'='*int(percent/length_div)}", end='')

        term_colour("native")               # The percentage string.
        print(pc_str, end='')

        term_colour("light red")            # The end of the bar.
        print(f"{'-'*(length-int(percent/length_div)-(len(pc_str)+2))}", end='')

        term_colour("native")               # The suffix and end of the bounding box.
        print("]"+suffix, end='\n' if (percent == 100.0) else '')

if __name__ == "__main__":
	main()
