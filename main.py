import clang.cindex
import sys

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

# Gets clang to start parsing the file, and generate an Abstract Syntax Tree.
idx = clang.cindex.Index.create()
tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                unsaved_files=[('tmp.cpp', s.read())],  options=0)

# Remember the amount of tokens we come across. We'll print it later.
num_tokens = 0

# Generate a textual representation of the AST, in AST.txt.
f = open("AST.txt", "w")
for t in tu.get_tokens(extent=tu.cursor.extent):
    f.write(t.spelling + " ")
    f.write("<- type = " + t.kind.name + "\n")
    # print(t.kind.value) # Prints the numerical value of each token
    num_tokens += 1

# Print the number of tokens.
print("\nNumber of tokens in given file:", num_tokens, "\n")