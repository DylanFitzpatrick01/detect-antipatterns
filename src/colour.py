import os, sys

# Change the colour of the terminal, using ANSI colour codes.
# The first input string is the text colour, The second is the background.
# Only changes colours if we're outputting to a terminal.
def term_colour(text: str="native", background: str="native") -> str:

    os.system("") # Gets ANSI colour codes working on windows.

    # using a terminal...
    if (sys.stdout.isatty()):
        # Reset the terminal colour scheme...
        print(f'\033[{text_colours[text]};{background_colours[background]}m', end='')


# A list of ANSI colour codes for terminals. 'native' = default colours
text_colours = {
    "black"        : '30',
    "red"          : '31',
    "green"        : '32',
    "yellow"       : '33',
    "blue"         : '34',
    "purple"       : '35',
    "cyan"         : '36',
    "light grey"   : '37',
    "dark grey"    : '90',
    "light red"    : '91',
    "light green"  : '92',
    "light yellow" : '93',
    "light blue"   : '94',
    "light purple" : '95',
    "light cyan"   : '96',
    "white"        : '97',
    "native"       : '39'
}
background_colours = {
    "black"        : '40',
    "red"          : '41',
    "green"        : '42',
    "yellow"       : '43',
    "blue"         : '44',
    "purple"       : '45',
    "cyan"         : '46',
    "light grey"   : '47',
    "dark grey"    : '100',
    "light red"    : '101',
    "light green"  : '102',
    "light yellow" : '103',
    "light blue"   : '104',
    "light purple" : '105',
    "light cyan"   : '106',
    "white"        : '107',
    "native"       : '49'
}