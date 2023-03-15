import re, os
from clang.cindex import TranslationUnit, SourceLocation, SourceRange
from typing import Union


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
    def display(self):

        # Our colours! Light red for error, yellow for warning.
        colours = { "error"      : "light red",
                    "warning"    : "yellow",
                    "greyed out" : "dark grey" }

        # Gets the C++ file, removes comments, then saves it  as an array, with one entry per line.
        lines = remove_comments("".join(open(self.tu.spelling).readlines()[0:])).splitlines()

        # for: the line before the error line (if it exists), the error line,
        # and the line after the error line (if it exists).
        for index in range(max(self.location.start.line-1,1),min(self.location.end.line+2,len(lines)+1)):

            # If the line isn't in our location, grey it out!
            if (index < self.location.start.line or index > self.location.end.line):
                term_colour(colours["greyed out"])
                print(f"{index}: {lines[index-1]}")
                term_colour("native")

            # Otherwise, print the line number in our native colour, and the line in our severity colour.
            else:
                term_colour("native")
                print(f"{index}: ", end='')
                term_colour(colours[self.severity])
                print(lines[index-1], end= '' if index == self.location.end.line else '\n')

            # If it's the last line in our location, display the error message.
            if index == self.location.end.line:
                
                term_colour("black", colours[self.severity])
                print(f"\n{' '*(len(str(index))+2)}^ ", end='')
                print(f"{'-'*8}In '{self.tu.spelling}', starting at ({self.location.start.line}, {self.location.start.column}){'-'*8}")
                print(f"{' '*(len(str(index))+4)}" + self.message.replace("\n", "\n"+" "*(len(str(index))+4)), end='')
                print('\033[m', end='\n')


# Inspired by https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
# Removes C-Style comments in a multi-line string.
def remove_comments(text):
    return re.sub(
        re.compile(r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE), "", text
    )


# Change the colour of the terminal, using ANSI colour codes.
# The first input string is the text colour, The second is the background.
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

# A list of ANSI colour codes for terminals. 'native' = default colours
text_colours = {
    "black"        : '\033[30m',
    "red"          : '\033[31m',
    "green"        : '\033[32m',
    "yellow"       : '\033[33m',
    "blue"         : '\033[34m',
    "purple"       : '\033[35m',
    "cyan"         : '\033[36m',
    "light grey"   : '\033[37m',
    "dark grey"    : '\033[90m',
    "light red"    : '\033[91m',
    "light green"  : '\033[92m',
    "light yellow" : '\033[93m',
    "light blue"   : '\033[94m',
    "light purple" : '\033[95m',
    "light cyan"   : '\033[96m',
    "white"        : '\033[97m',
}
background_colours = {
    "black"        : '\033[40m',
    "red"          : '\033[41m',
    "green"        : '\033[42m',
    "yellow"       : '\033[43m',
    "blue"         : '\033[44m',
    "purple"       : '\033[45m',
    "cyan"         : '\033[46m',
    "light grey"   : '\033[47m',
    "dark grey"    : '\033[100m',
    "light red"    : '\033[101m',
    "light green"  : '\033[102m',
    "light yellow" : '\033[103m',
    "light blue"   : '\033[104m',
    "light purple" : '\033[105m',
    "light cyan"   : '\033[106m',
    "white"        : '\033[107m',
    "native"       : '\033[m'
}