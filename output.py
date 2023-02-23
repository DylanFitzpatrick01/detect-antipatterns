import os, re

# given a filename, a (line, column) tuple, and an error string,
# show the error message pointing at our location.
# Multi-line error messages are supported.
def print_error(filename: str, location: tuple, error_msg: str, severity: str="error"):

    # Gets the C++ file, removes comments, then saves it 
    # as an array, with one entry per line.
    lines = remove_comments("".join(open(filename).readlines()[0:])).splitlines()

    highlight_colour = "light red" if (severity=="error") else "yellow"
    
    if (location[0] <= len(lines) and location[1] <= len(lines[location[0]-1])):
        print()

        # If we have a line before our error, print it!
        colour("dark grey")
        print((str(location[0]-1) + ": " +
            lines[location[0]-2] + "\n") if (location[0] > 1) else "",
            end='')
        colour("native")

        # Print the non-error part of the line our location points to!
        print(str(location[0]) + ": " +
              lines[location[0]-1][0:location[1]-1],
              end='')
        
        # Print the rest of the line our location points to,
        # with an error colour. 
        colour(background=highlight_colour)
        print(lines[location[0]-1][location[1]-1:len(lines[location[0]-1])],
              end='')
        colour("native")

        # Print our error message, offset to align with the error.
        print("\n" + (" "*(location[1]-1 + len(str(location[0]) + ": "))),
              end='')
        colour(highlight_colour)
        print("^" + error_msg.replace("\n", "\n" + " "*(location[1] + len(str(location[0]) + ": "))))
        colour("native")

        # If we have a line after our error, print it!
        colour("dark grey")
        print((str(location[0]+1) + ": " +
              lines[location[0]] + "\n") if (len(lines) > location[0]) else "",
              end='')
        colour("native")
        print()

    # If we call for a location that isn't in the file, complain!
    else:
        colour(background="light red")
        print("ERROR in print_error(): location (" + 
              str(location[0]) + ", " + str(location[1]) + 
              ") does not exist in \"" + filename + "\".")
        colour("native")


# Change the colour of the terminal.
# The first input string is the text colour, The second is the background.
# A list of supported colours can be found below.
def colour(text: str="native", background: str="native"):

    os.system("") # Gets ANSI colour codes working on windows.

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
def remove_comments(text):
    return re.sub(re.compile(r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"', re.DOTALL | re.MULTILINE), "", text)

if __name__ == "__main__":
    print_error("test.cpp", (7,5), "Test!\nA multi-line error message.\nCool!")