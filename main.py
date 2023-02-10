import clang.cindex
import sys

def main():

    # Attempt to get a filename from the command line args.
    # If that fails, ask the user.
    # If both fail, give up.
    s = ""
    try:
        if (len(sys.argv) > 1):
            s = open(sys.argv[1], "r")
        else:
            s = open(input("Enter the name of the file you'd like to analyse\n > "), "r")
    except FileNotFoundError:
        print("FILE DOES NOT EXIST!\n")
        exit()

    # Gets clang to start parsing the file, and generate
    # a translation unit with an Abstract Syntax Tree.
    idx = clang.cindex.Index.create()
    tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                    unsaved_files=[('tmp.cpp', s.read())],  options=0)

    # Generate a textual representation of the AST, in AST.txt.
    save_ast(tu, "AST.txt")

    # Print the number of tokens.
    print("\nNumber of tokens in given file:", count_tokens(tu), "\n")



# --------FUNCTIONS-------- #

# Saves the AST of a translation unit into a text file with
# a given filename.
def save_ast(translation_unit, filename):
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