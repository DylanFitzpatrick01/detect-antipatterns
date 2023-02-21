import clang.cindex
import sys

def main():

    # Attempt to get a filename from the command line args.
    # If that fails, ask the user.
    # If both fail, give up.
    s = ""
    try:
        if (len(sys.argv) > 1):
            s = sys.argv[1]
        else:
            s = input("Enter the name of the file you'd like to analyse\n > ")
        open(s)
    except FileNotFoundError:
        print("FILE DOES NOT EXIST!\n")
        exit()

    # Gets clang to start parsing the file, and generate
    # a translation unit with an Abstract Syntax Tree.
    idx = clang.cindex.Index.create()
    tu = idx.parse(s, args=['-std=c++11'])

    # Generate a textual representation of the tokens, in pubmut.txt.
    save_tokens(tu, "pubmut.txt")

    # Traverse the AST
    traverse(tu.cursor)

    # Print the number of tokens.
    print("\nNumber of tokens in given file:", count_tokens(tu), "\n")


# --------FUNCTIONS-------- #

# Traverses Clangs cursor tree. A cursor points to a piece of code,
# and has extremely useful values and functions. The cursor tree is
# a generic tree, and this function runs for every node in that tree.
# https://libclang.readthedocs.io/en/latest/#clang.cindex.Cursor
# https://www.geeksforgeeks.org/generic-treesn-array-trees/
#
def traverse(cursor: clang.cindex.Cursor):

    c: clang.cindex.Cursor
    for c in cursor.get_children():

        # This line makes sure that the line of code our cursor points to
        # is in the same file that our translation unit is analysing.
        #
        # This means no cursors from header files! If this wasn't here,
        # we'd be looking at the cursors of HUNDREDS of microsoft C++ 
        # std functions.
        #
        if(str(cursor.translation_unit.spelling) == str(c.location.file)):

            # -------DETECTION LOGIC HERE!-------
            # Check out the Cursor class for helpful info.
            # https://libclang.readthedocs.io/en/latest/#clang.cindex.Cursor
            # 
            # This runs for EVERY cursor in the tree! Write a bunch of
            # if statements, etc., to detect what you're looking for,
            # then call whatever functions you need!
            # 
            # Keep logic in this function light. You should call a function
            # outside of this one if you're running bulky code. Don't put
            # it here! Just simple if-else statements, etc.
            #
            #-------DELETE ME!-------
            print("\nDisplay name: ",str(c.displayname) + 
                  "\n\tAccess specifier:",str(c.access_specifier) + 
                  "\n\tLocation: ("+str(c.location.line)+", "+str(c.location.column)+")"
                  "\n\tKind:",str(c.kind)
                 )
            #-------DELETE ME!-------
            
            traverse(c) # Recursively traverse the tree.

# Saves the tokens of a translation unit into a text file with
# a given filename.
def save_tokens(translation_unit, filename):
    file = open(filename, "w")
    for token in translation_unit.get_tokens(extent=translation_unit.cursor.extent):
        file.write(token.spelling + " ")
        file.write("<- type = " + token.kind.name + "\n")

# Counts the number of tokens in the AST of a translation unit.
def count_tokens(translation_unit):
    num_tokens = 0
    for token in translation_unit.get_tokens(extent=translation_unit.cursor.extent):
        # print(token.kind.value) # Prints the numerical value of each token
        num_tokens += 1
    return num_tokens

if __name__ == "__main__":
    main()