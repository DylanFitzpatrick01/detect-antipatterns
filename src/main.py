import clang.cindex
import sys, os, importlib, argparse, inspect, pathlib
from typing import List
from formalCheckInterface import FormalCheckInterface
from alerts import Alert
clang.cindex.Config.set_library_file('C:/msys64/mingw64/bin/clang.exe')

def main():
    # Get our argmuents namespace from the user.
    args = init_argparse()

    # Import all of our checks!
    #==============================================#
    check_list = list()
    # For all of the python files in the checks directory...
    for file in [x for x in os.listdir(args.checks_dir) if x.endswith('.py')]:

        # Get the associated python module...
        sys.path.append(str(args.checks_dir))
        check_module = importlib.import_module(file.removesuffix('.py'))

        # Look at all of the classes in that module...
        for name_local in dir(check_module):
            check_class = getattr(check_module, name_local)

            # If it inherits from our check interface, then append an
            # object of it to our check list!
            if (inspect.isclass(check_class) and issubclass(check_class,FormalCheckInterface)):
                check_list.append(check_class())
    #==============================================#
    
    alerts: List[FormalCheckInterface] = list()

    # Run every check on every cursor of every file.
    #==============================================#
    for index, file in enumerate(args.locations):
        # Progress bar for terminals.
        progress_bar(index,len(args.locations),40,suffix=' of files analysed')

        # Gets clang to start parsing the file, and generate
        # a translation unit with an Abstract Syntax Tree.
        idx = clang.cindex.Index.create()
        tu = idx.parse(file)

        # Traverse the AST
        alerts.extend(traverse(tu.cursor, check_list))

    # Complete progress bar, as we don't get to write again
    # until we're out of the loop.
    progress_bar(1,1,40,suffix=' of files analysed')
    #==============================================#

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


# Returns an argument parser initialised with the users arguments.
# Automatically rejects nonexistent files/directories and unsupported file types.
def init_argparse() -> argparse.ArgumentParser:

    global checks_dir

    # Setting up the argument parser.
    parser = argparse.ArgumentParser(
        description='Detects common C++ concurrency anti-patterns and malpractices pre-compile.',
        epilog='If you intend for the data of this program to be read by a person, verbosity and '
               'colour are "encouraged" (NECESSARY). The default ouput is designed for log files; to '
               'be picked up by another program, NOT TO BE READ BY REAL PEOPLE.'
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
    parser.add_argument('-c', '--colour',
                        action=  "store_true",
                        help=    'add colour to output, for ease of reading')

    
    args = parser.parse_args()

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
                args.locations, [os.path.join(loc,x) for x in os.listdir(loc) if x.endswith('.cpp')]
            )))
        
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

# Progress bar!
def progress_bar(amount:float,max:float,length:int,prefix='',suffix:str=''):
    if sys.stdout.isatty():                 # If we're outputting to a terminal...
        percent = (amount*100)/max          # Get our percentage
        pc_str = '{:.1f}%'.format(percent)  # Make a formatted percentage string
        length_div = 100/(length-8)         # Get the right divisor so that we achieve our desired length.
        string = f"[\b \r{prefix}[{'='*int(percent/length_div)}{pc_str}{'-'*(length-int(percent/length_div)-(len(pc_str)+2))}]"+suffix
        end = '\n' if (percent == 100.0) else ''
        print(string, end=end)

if __name__ == "__main__":
    main()
