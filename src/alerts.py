import re, os
from clang.cindex import TranslationUnit, SourceLocation, SourceRange
from typing import Union
from colour import term_colour


# A class for to hold information about something that's gone wrong.
#
# Alert.display() shows the user what's wrong (fancily).
#
class Alert:

    # Constructor!
    def __init__(self,
                 tu: TranslationUnit,
                 location: Union[tuple, SourceLocation, SourceRange],
                 message: str,
                 severity: str="error") -> None:

        # Initialise the values of the Alert.
        self.tu = tu
        self.location = location
        self.message = message
        self.severity = severity

        # If the location is a tuple or SourceLocation, turn it into a SourceRange.
        if (type(location) == tuple):
            start = SourceLocation.from_position(tu, tu.get_file(tu.spelling), location[0], location[1])
            end = SourceLocation.from_position(tu, tu.get_file(tu.spelling), location[0], -1)
            self.location = SourceRange.from_locations(start, end)
        if (type(location) == SourceLocation):
            end = SourceLocation.from_position(tu, tu.get_file(tu.spelling), location.line, -1)
            self.location = SourceRange.from_locations(location, end)


    # Displays our Alert (Fancily)
    def display(self, verbosity_count):

        # Our colours! Light red for error, yellow for warning.
        colours = { "error"      : "light red",
                    "warning"    : "yellow", }

        # Gets the C++ file, removes comments, then saves it  as an array, with one entry per line.
        lines = remove_comments("".join(open(self.tu.spelling).readlines()[0:])).splitlines()

        # Fancy
        if (verbosity_count >= 1):
            # for: the line before the error line (if it exists), the error line,
            # and the line after the error line (if it exists).
            for index in range(max(self.location.start.line-1,1),min(self.location.end.line+2,len(lines)+1)):

                # Print the line number in our native colour, and the line in our severity colour.
                term_colour("native")
                print(f"{index}: ", end='')
                term_colour(colours[self.severity])
                print(lines[max(0,index-1)], end='\n')

                # If it's the last line in our location, display the error message.
                if index == self.location.end.line:
                    term_colour("black", colours[self.severity])
                    print(f"{' '*(len(str(index))+2)}{'-'*8}{self.severity.upper()}: '{os.path.basename(self.tu.spelling)}', ({self.location.start.line}, ", end='')
                    print(f"{self.location.start.column})-({self.location.end.line}, {self.location.end.column}){'-'*8} ")
                    print(f"{' '*(len(str(index))+2)}^ " + self.message.replace("\n", " \n"+" "*(len(str(index))+4)) + " ", end='')
                    print('\033[m', end='\n')
                    print()
                    return
        # Unfancy
        else:
            term_colour(colours[self.severity])
            print(f"{self.severity.upper()}: '{os.path.basename(self.tu.spelling)}' ({self.location.start.line}, ", end='')
            print(f"{self.location.start.column})-({self.location.end.line}, {self.location.end.column}): ", end='')
            term_colour("native")
            print(self.message.replace("\n", "\\n"),)


# Inspired by https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
# Removes C-Style comments in a multi-line string.
def remove_comments(text):
    return re.sub(
        re.compile(r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE), "", text
    )
