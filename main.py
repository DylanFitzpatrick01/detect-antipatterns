import clang.cindex
clang.cindex.Config.set_library_file('C:/Program Files/LLVM/bin/libclang.dll')
import sys
from datapair import *

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
    dataPairs = generate_pairs(tu)
    # Generate a textual representation of the AST, in AST.txt.
    save_ast(tu, "pubmut.txt")

    # Print the number of tokens.
    print("\nNumber of tokens in given file:", count_tokens(tu), "\n")

    # Call public-mutex-members method
    public_mutex_members(dataPairs)


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

def generate_pairs(translation_unit):
    dataPairs = []
    for token in translation_unit.get_tokens(extent=translation_unit.cursor.extent):
        spelling = token.spelling
        name = token.kind.name
        data = DataPair(spelling, name)
        dataPairs.append(data)
    
    return dataPairs

def public_mutex_members(dataPairs):
    is_public = False
    war = False
    curly_brackets_count = 0

    for index,pair in enumerate(dataPairs):
        if pair.variable == "public":
            is_public = True
        elif pair.variable == "private":
            is_public = False
        elif pair.variable == "{":
            curly_brackets_count = curly_brackets_count + 1
        elif pair.variable == "}":
            curly_brackets_count = curly_brackets_count - 1
        elif is_public and curly_brackets_count == 1 and pair.variable == "mutex":
            print("public_mutex_members - Are you sure you want to have a public mutex called " + dataPairs[index+1].variable)
            war = True

    if not war:
        print("public_mutex_members - No problem found")


if __name__ == "__main__":
    main()