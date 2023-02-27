import shutil
import string
import struct
from tkinter import Variable
import clang.cindex
import sys
from datapair import *
from output import *
from cursorSearch import *
from missingUnlock import *
from locks import *
clang.cindex.Config.set_library_file('C:/Program Files/LLVM/bin/libclang.dll')

def main():

    # Attempt to get a filename from the command line args.
    # If that fails, ask the user.
    # If both fail, give up.
    quit = False
    while quit == False:
        
        exist = True
        s = ""
        try:
            if (len(sys.argv) > 1):
                s = sys.argv[1]
            else:
                s = input("\nEnter the name of the file you'd like to analyse or 'quit' to quit\n > ")
            open(s)

            # Make a txt copy of cpp code
            shutil.copy(s, 'c++.txt')

        except FileNotFoundError:
            exist = False
            if s == "quit":
                quit = True
            else:    
                print("FILE DOES NOT EXIST!\n")

        if exist == True:
            choice = ""
            okInput = False
            choice = 0

            print("Choose what analysis you would like to run by selecting from the following options:")
            print("Press 1 for public mutex members check")
            print("Press 2 for immutable objects check")
            print("Press 3 for manual lock/unlock check")
            print("Press 4 for mutex order and out of scope mutex call checks")

            while okInput == False:
                choose = input("Please enter a number between 1 and 4:\n")

                if choose == "1" or choose == "2" or choose == "3" or choose == "4": 
                    choice = choose
                    okInput = True
                else:
                    print("Error invalid input...") 
            

            # Gets clang to start parsing the file, and generate
            # a translation unit with an Abstract Syntax Tree.
            idx = clang.cindex.Index.create()
            tu = idx.parse(s, args=['-std=c++11'])

            dataPairs = generate_pairs(tu)
            
            # Generate a textual representation of the tokens, in pubmut.txt.
            save_tokens(tu, "pubmut.txt")

            # Traverse the AST
            traverse(tu.cursor)
    
            # Call methods
            print("\n---------------------\n")

            if choice == "1":
                print("Checking for public mutex members...\n")   
                #public_mutex_members(dataPairs)
            elif choice == "2":
                print("Checking for immutable objects...\n") 
                immutable_objects(dataPairs)
            elif choice == "3":
                print("Checking for missing manual locks/unlocks...\n") 
                missing_unlock(tu)
            elif choice == "4":
                print("Checking the order of mutexes and whether mutexes are called out of scope\n")
                tests(s, False, True)   
            else:
                print("Shouldn't get here.")     

            # Print the number of tokens.
            # print("\nNumber of tokens in given file:", count_tokens(tu), "\n")

    print("Program terminated.")

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
            #print("\nDisplay name: ",str(c.displayname) +
            #    "\n\tAccess specifier:",str(c.access_specifier) +
            #    "\n\tLocation: ("+str(c.location.line)+", "+str(c.location.column)+")"
            #    "\n\tKind:",str(c.kind)
            #  )
            #-------DELETE ME!-------
            public_mutex_members_API(c)
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

def generate_pairs(translation_unit):
    dataPairs = []
    for token in translation_unit.get_tokens(extent=translation_unit.cursor.extent):
        spelling = token.spelling
        name = token.kind.name
        data = DataPair(spelling, name)
        dataPairs.append(data)

    # generate line number for each pair using txt file
    txt = open('c++.txt', 'r')
    line_counter = 1
    line_string = txt.readline()
    for index, pair in enumerate(dataPairs):
        if dataPairs[index].variable in line_string:
            dataPairs[index].line_number = line_counter
            if line_string.endswith(dataPairs[index].variable+"\n"):
                line_counter += 1
                line_string = txt.readline()
        else:
            while not(dataPairs[index].variable in line_string):
                line_counter += 1
                line_string = txt.readline()
            dataPairs[index].line_number = line_counter
    #for pair in dataPairs:
        #print(pair.variable + " " + str(pair.line_number))

    txt.close()

    # generate line number for each pair using txt file
    txt = open('c++.txt', 'r')
    line_counter = 1
    line_string = txt.readline()
    for index, pair in enumerate(dataPairs):
        if dataPairs[index].variable in line_string:
            dataPairs[index].line_number = line_counter
            if line_string.endswith(dataPairs[index].variable+"\n"):
                line_counter += 1
                line_string = txt.readline()
        else:
            while not(dataPairs[index].variable in line_string):
                line_counter += 1
                line_string = txt.readline()
            dataPairs[index].line_number = line_counter
    #for pair in dataPairs:
        #print(pair.variable + " " + str(pair.line_number))

    txt.close()
    return dataPairs

def public_mutex_members_API(cursor: clang.cindex.Cursor):
    if str(cursor.access_specifier) == "AccessSpecifier.PUBLIC":
        #print(str(cursor.displayname) + " Public")
        count = 0
        contains = False
        for cursor1 in cursor.get_children():
            count += 1
            if str(cursor1.displayname) == "class std::mutex" and str(cursor1.kind) == "CursorKind.TYPE_REF":
                contains = True
        if contains and count == 2:
            print("public_mutex_members - Are you sure you want to have a public mutex called " + str(
                cursor.displayname) + ", Line - " + str(cursor.location.line))

def public_mutex_members(dataPairs):
    is_public = False
    war = False
    curly_brackets_count = 0

    for index, pair in enumerate(dataPairs):
        if pair.variable == "public":
            is_public = True
        elif pair.variable == "private" or pair.variable == "protected":
            is_public = False
        elif pair.variable == "{":
            curly_brackets_count = curly_brackets_count + 1
        elif pair.variable == "}":
            curly_brackets_count = curly_brackets_count - 1
        elif is_public and curly_brackets_count == 1 and pair.variable == "mutex":
            print("public_mutex_members - Are you sure you want to have a public mutex called " + dataPairs[index+1].variable + ", Line - " + str(dataPairs[index+1].line_number))
            war = True

    if not war:
        print("No errors found for public mutex members.")

def immutable_objects(dataPairs):
    is_struct = False
    constCount = 0
    varCount = 0
    threshold = 0.25

    for index, pair in enumerate(dataPairs):
        if pair.variable == "struct":
            is_struct = True
        else:
            if is_struct == True:
                if  pair.variable == "}":
                    is_struct = False
                else:   
                    if pair.variable == "const":
                        constCount+=1
                    elif pair.variable == "int" or pair.variable == "double" or pair.variable == "string" or pair.variable == "char" or pair.variable == "bool":
                        varCount+=1
    notConst = 1

    if constCount > 0 and varCount > 0:
        notConst = 1 - (constCount / varCount)

    if notConst <= threshold and notConst > 0:
        prettier = round(notConst, 4) * 100
        print(prettier, "% of your variables in this struct are not constant.")
        print("We suspect you may want to make this class immutable, however at the moment it isn't.")
        print("We recommend you examine the code before proceeding.")

    else:
        print("No errors found for immutable objects.")   


def missing_unlock(tu):
    search_string = ".lock()"
    errors = False
    #print("\nSearching for {:s}...".format(search_string))
    found_cursors = cursor_search(tu.cursor, search_string)
    for cursor in found_cursors:
    # print("cursor covers the following range of text:", cursor.extent)
        caller = findCaller(cursor, "lock")
        #print(t)
        result = isUnlockCalled(cursor, caller)
        if result == True:
            print("")
        else:
            print(" Manual lock was found within the following scope : \n Line ", str(cursor.extent.start.line),
             " -> Line ", str( cursor.extent.end.line), 
             "\n No manual unlock was detected within the same scope,\n are you missing a call to '", caller, ".unlock()'?")
            errors = True

    if errors == False:
        print("No errors found for missing manual unlocks.")

def check_lock_order(order):
    held_locks = set()
    for mutex in order:
        if mutex in held_locks:
            print("Error: mutex", mutex, "is already held")
        else:
            held_locks.add(mutex)
    for mutex in reversed(order):
        held_locks.remove(mutex)               

if __name__ == "__main__":
    main()
