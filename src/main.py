import clang.cindex
import sys, os, importlib.util, argparse, io
from typing import List
from formalCheckInterface import FormalCheckInterface
from alerts import Alert
clang.cindex.Config.set_library_file('C:/Program Files/LLVM/bin/libclang.dll')

# Relative directory that contains our check files.
checks_dir = '../checks'

def main():
    args = init_argparse()

    # Gets clang to start parsing the file, and generate
    # a translation unit with an Abstract Syntax Tree.
    idx = clang.cindex.Index.create()
    tu = idx.parse(args.location)

    # Import all of our checks!
    try:
        check_list = list()
        for file in os.listdir(os.path.abspath(os.path.join(os.path.dirname( __file__ ), checks_dir))):
            if (file.endswith(".py")):
                spec = importlib.util.spec_from_file_location(file.removesuffix(".py"), os.path.abspath(os.path.join(os.path.dirname( __file__ ), checks_dir, file)))
                check_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(check_module)
                check_list.append(check_module.Check())
    except FileNotFoundError:
        print(f"checks_dir '{checks_dir}' does not exist! Make sure it's a relative directory to main.py!")
        exit()

    # Traverse the AST
    alerts = traverse(tu.cursor, check_list)

    # print to console, with as much info / colour as requested.
    for alert in alerts:
        alert.display(args.verbose, args.colour)
        
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
def traverse(cursor: clang.cindex.Cursor, check_list: List[FormalCheckInterface]) -> List[Alert]:

    alerts: List[Alert] = list()

    # For every cursor in the AST...
    child_cursor: clang.cindex.Cursor
    for child_cursor in cursor.walk_preorder():

        # This line makes sure that the line of code our cursor points to
        # is in the same file that our translation unit is analysing.
        #
        # This means no cursors from header files! If this wasn't here,
        # we'd be looking at the cursors of HUNDREDS of microsoft C++ 
        # std functions.
        #
        if(str(cursor.translation_unit.spelling) == str(child_cursor.location.file)):

            # -------DETECTION LOGIC HERE!-------
            # Runs all of our checks, on every cursor in the tree.
            # Adds the alerts they raise to the alerts pile!
            for check in check_list:
                alerts.extend(check.analyse_cursor(child_cursor))
    
    # Complain!
    return alerts

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Detects common C++ concurrency anti-patterns and malpractices pre-compile.',
    )
    parser.add_argument('location',
                        nargs=   '?',
                        type=    str,
                        default= sys.stdin,
                        help=    'The file (or directory of files) to analyse, reads stdin by default')
    parser.add_argument('-v', '--verbose',
                        action=  'count',
                        default= 0,
                        help= 'Increases output verbosity level by one')
    parser.add_argument('-c', '--colour',
                        action=  "store_true",
                        help= 'Add colour to output, for ease of reading (RECOMMENDED)')
    
    args = parser.parse_args()
    
    # Check if we're reading our file/directory from stdin. If we're getting
    # our stdin from the user, display some helpful text.
    if type(args.location) == io.TextIOWrapper:
        if not os.isatty(sys.stdin.fileno()):
            setattr(args, "location", args.location.read())
        else:
            setattr(args, "location",
                    input("\nEnter the name of the file you'd like to analyse:\n > "))

    # Make sure infile/indir actually exists.
    if not (os.path.isfile(args.location) or os.path.isdir(args.location)):
        raise SystemExit(f"error: FILE/DIRECTORY '{args.location}' DOES NOT EXIST!")
    
    return args

if __name__ == "__main__":
    main()
