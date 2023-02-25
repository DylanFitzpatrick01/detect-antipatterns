import os, re
from clang.cindex import TranslationUnit, SourceLocation, SourceRange
import clang
from colours import *

# prints the given error message in a fancy way.
# 
def print_error(tu: TranslationUnit,
                location: tuple | SourceLocation | SourceRange,
                message: str,
                severity: str="error"):

    # Our colours! Light red for error, yellow for warning.
    colours = { "error"      : "light red",
                "warning"    : "yellow",
                "greyed out" : "dark grey" }
    
    # If location is a tuple or SourceLocation, turn them into a SourceRange.
    if (type(location) == tuple):
        start = SourceLocation.from_position(tu, tu.get_file(tu.spelling), location[0], location[1])
        end = SourceLocation.from_position(tu, tu.get_file(tu.spelling), location[0], -1)
        location = SourceRange.from_locations(start, end)
    if (type(location) == SourceLocation):
        end = SourceLocation.from_position(tu, tu.get_file(tu.spelling), location.line, -1)
        location = SourceRange.from_locations(location, end)

    # Gets the C++ file, removes comments, then saves it  as an array, with one entry per line.
    lines = remove_comments("".join(open(tu.spelling).readlines()[0:])).splitlines()

    # Tell the user the file name and location.
    term_colour(colours["greyed out"])
    print(f"{'-'*8}In '{tu.spelling}', starting at ({location.start.line}, {location.start.column}){'-'*8}")

    # for: the line before the error line (if it exists), the error line,
    # and the line after the error line (if it exists).
    for index in range(max(location.start.line-1,0),min(location.end.line+2,len(lines))):

        # !!!!!!!!!!!!!!!!!!!!UNFINISHED!!!!!!!!!!!!!!!!!!!!!!!!!
        # Comp. labs closed mid-session! Saving through github for now.
        # I'll get back to it tomorrow.
        # Future commit message:
        # Revised output.py
        # Output.py now integrates much better with the libclang library:
        # - The file is referenced using a TranslationUnit, which will be the main way we reference files going forward.
        # - The location can either be a tuple - (line, column), a SourceLocation (clang's line-column reference class), or a SourceRange (Two SourceLocation values - start & end).
        # - If the type is a tuple or SourceLocation, we automatically convert them to a single-line SourceRange object.
        # -  

        if (index < location.start.line or index > location.end.line):
            # Print non-location lines in dark grey.
            term_colour(colours["greyed out"])
            print(f"{index}: {lines[index-1]}")
            term_colour("native")
        else:
            print(f"{index}: ", end='')
            # Print a line within 'location'.
            if (index == location.start.line):
                term_colour(colours[severity])
                print(lines[index-1][location.start.column-1:len(lines[location.start.column])], end='\033[m')
                print()
            elif (index < location.end.line):
                term_colour(colours[severity])
                print(lines[index-1], end='\033[m')
                print()
            else:
                # Print our error message, offset to align with the error.
                print(f"\n{' '*(location.start.column-1+len(str(index+1))+2)}", end='')
                term_colour(background=colours[severity])
                print("^" + message.replace("\n", "\n"+" "*(location.start.column+len(str(index+1))+2)), end='')
                term_colour("native")
                print()

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# Change the colour of the terminal, using ANSI colour codes.
# The first input string is the text colour, The second is the background.
# A list of supported colours can be found in 'colours.py'.
def term_colour(text: str="native", background: str="native"):

    os.system("") # Gets ANSI colour codes working on windows.

    # If we want our default text colours...
    if (text == "native"):
        # Reset the terminal colour scheme...
        print('\033[m', end='')
        # Apply our background color
        print(background_colours[background], end='')
    
    # Otherwise, apply background colour first.
    else:
        print(background_colours[background], end='')
        print(text_colours[text], end='')


# Inspired by https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
# Removes C-Style comments in a multi-line string.
def remove_comments(text):
    return re.sub(
        re.compile(r'\s*//.*?$|\s*/\*.*?\*/|\s*\'(?:\\.|\s*[^\\\'])*\'|\s*"(?:\\.|\s*[^\\"])*"',
        re.DOTALL | re.MULTILINE), "", text
    )
    
if __name__ == "__main__":
    idx = clang.cindex.Index.create()
    tu = idx.parse("unlock.cpp", args=['-std=c++11'])
    start = SourceLocation.from_position(tu, tu.get_file(tu.spelling), 5, 7)
    end = SourceLocation.from_position(tu, tu.get_file(tu.spelling), 10, 3)
    location = SourceRange.from_locations(start, end)
    print_error(tu, location, "YO!")