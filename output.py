import os, re
from typing import Union
from clang.cindex import TranslationUnit, SourceLocation, SourceRange
from colours import *

# prints the given error message in a fancy way.
# 
def print_error(tu: TranslationUnit,
                location: Union[tuple, SourceLocation, SourceRange],
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

        # I won't lie, this code is messy. I'll update it soon!
        if (index < location.start.line or index > location.end.line):
            term_colour(colours["greyed out"])
            print(f"{index}: {lines[index-1]}")
            term_colour("native")
        else:
            print('\033[m', end='')
            print(f"{index}: ", end='')
            if index == location.start.line:
                print(lines[index-1][0:location.start.column-1], end=text_colours[colours[severity]])
                print(lines[index-1][location.start.column-1:len(lines[index-1])], end='')
                if location.start.line == location.end.line:
                    term_colour("black", colours[severity])
                    print(f"\n{' '*(location.start.column+len(str(index))+2)}", end='')
                    print("^ " + message.replace("\n", "\n"+" "*(location.start.column+len(str(index))+4)))
                    print('\033[m', end='')
                    continue
                print()
            elif index == location.end.line:
                term_colour(colours[severity])
                print(lines[index-1][0:location.end.column], end='\033[m')
                print(lines[index-1][location.end.column:len(lines[index-1])], end='')
                term_colour("black", colours[severity])
                print(f"\n{' '*(len(str(index))+2)}", end='')
                print("^ " + message.replace("\n", "\n"+" "*(len(str(index))+4)))
                print('\033[m', end='')
            else:
                term_colour(colours[severity])
                print(lines[index-1])


# Change the colour of the terminal, using ANSI colour codes.
# The first input string is the text colour, The second is the background.
# A list of supported colours can be found in 'colours.py'.
def term_colour(text: str="native", background: str="native"):

    os.system("") # Gets ANSI colour codes working on windows.

    # If we want our default text colours w/ custom background...
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