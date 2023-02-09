import clang.cindex
import sys

s = ""
if (len(sys.argv) > 1):
    s = open(sys.argv[1], "r")
else:
    try:
        s = open(input("Enter the name of the file you'd like to analyse\n > "), "r")
    except FileNotFoundError:
        print("FILE DOES NOT EXIST!\n")
        exit()

idx = clang.cindex.Index.create()
tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                unsaved_files=[('tmp.cpp', s.read())],  options=0)
f = open("AST.txt", "w")                
for t in tu.get_tokens(extent=tu.cursor.extent):
    f.write(t.spelling + " ")
    f.write("<- type = " + t.kind.name + "\n")
    print(t.kind.value)