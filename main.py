from collections import Counter
from gettext import translation
from itertools import count
import subprocess
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
import clang.cindex 
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
            index = clang.cindex.Index.create()
            translation_unit = index.parse(s)
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
                   
              
                    index =clang.cindex.Index.create()
                    tus = index.parse(s)
                    root = tus.cursor
                    immutable_objects_API(tus.cursor)





                    #var_decl_constcount = count_const_string_var_decls(root) # prints only const string variaables 
                    #print(var_decl_constcount)
                    #var_decl_count = count_string_var_decls(root)        # prints only  string variaables
           
                    #print(var_decl_count)


                    #var_decl_total_bool_count = count_bool_total_var_decls(root)
                    #print(var_decl_total_bool_count)

                    #var_decl_const_bool = count_const_bool_var_decls(root)
                    #print(var_decl_const_bool)

                    #var_decl_total_int_count = count_int_total_var_decls(root)
                    #print(var_decl_total_int_count)
                    #var_decl_const_int = count_const_int_var_decls(root)
                    #print(var_decl_const_int)

                    #total_double_count = count_const_double_var_decls(root)
                    #print(total_double_count)
                    #doublt_const_count = count_double_total_var_decls(root)
                    #print(doublt_const_count)

                    #total_char_count = count_char_total_var_decls(root)
                    #print(total_char_count)
                    #char_const_count = count_const_char_var_decls(root)
                    #print(char_const_count)
                    
                  
              
                    
                  


   


         

                
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
    
def immutable_objects_API(cursor: clang.cindex.Cursor):
    node = cursor
    constant_variable_count = 0
    variable_count = 0

    constant_variable_count +=count_const_string_var_decls(node)
    constant_variable_count += count_const_bool_var_decls(node)
    constant_variable_count += count_const_int_var_decls(node)
    constant_variable_count += count_const_double_var_decls(node)
    constant_variable_count += count_const_char_var_decls(node)

    #print(constant_variable_count)

    variable_count += count_string_var_decls(node)
    variable_count += count_bool_total_var_decls(node)
    variable_count += count_int_total_var_decls(node)
    variable_count += count_double_total_var_decls(node)
    variable_count += count_char_total_var_decls(node)

    #print(variable_count)


    threshold = 0.70


    ratio = constant_variable_count / variable_count

    if ( ratio) >= threshold:
        ratio = ratio * 100
        ratio = round(ratio,0)
        print(str(ratio) + "% of Variables are constant. This may cause an immutable object error")
    



def count_const_string_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if node.type.spelling == "const std::string":
            count += 1
            #print("std::string variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):

            count += count_const_string_var_decls(child)
    return count

def count_const_bool_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if  node.type.spelling == "const bool" :
            count += 1
            #print("bool variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_const_bool_var_decls(child)
    return count 

def count_const_int_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if  node.type.spelling == "const int" :
            count += 1
            #print("bool variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_const_int_var_decls(child)
    return count 

def count_const_double_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if  node.type.spelling == "const double" :
            count += 1
            #print("bool variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_const_double_var_decls(child)
    return count

def count_const_char_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if  node.type.spelling == "const char" :
            count += 1
            #print("bool variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_const_char_var_decls(child)
    return count   



def count_string_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if  node.type.spelling == "const std::string" or  node.type.spelling == "std::string" :
            count += 1
            #print(" std::string variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_string_var_decls(child)
    return count

def count_bool_total_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if  node.type.spelling == "const bool" or  node.type.spelling == "bool" :
            count += 1
            #print("bool variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_bool_total_var_decls(child)
    return count

def count_int_total_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if  node.type.spelling == "const int" or  node.type.spelling == "int" :
            count += 1
            #print("bool variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_int_total_var_decls(child)
    return count

def count_double_total_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
        if  node.type.spelling == "const double" or  node.type.spelling == "double" :
            count += 1
            #print("bool variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_double_total_var_decls(child)
    return count

def count_char_total_var_decls(node):
    count = 0
    if node.kind in [clang.cindex.CursorKind.VAR_DECL,
                     clang.cindex.CursorKind.FIELD_DECL,
                     clang.cindex.CursorKind.PARM_DECL]:
       if  node.type.spelling == "const char" or node.type.spelling == "char":
            count += 1
            #print("bool variable declaration: " + node.displayname)
    for child in node.get_children():
        if(str(child.translation_unit.spelling) == str(child.location.file)):
            count += count_char_total_var_decls(child)
    return count

           















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
