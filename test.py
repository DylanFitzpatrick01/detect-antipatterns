import clang.cindex
import main
from contextlib import suppress
from observer import *
from member_locked_in_some_methods import *
import os
import pytest

from missingUnlock import findCaller, isUnlockCalled

def test_save_tokens():

    # Our C++ 'file'
    cpp_file = '''
    int main(int x, int y)
    {
        return x + y
    }
    '''

    # The filename we'll be writing to.
    filename = "TESTING.txt"

    # Generate the translation unit from our 'file'.
    idx = clang.cindex.Index.create()
    tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                unsaved_files=[('tmp.cpp', cpp_file)],  options=0)
    
    # Save the AST of the translation unit
    main.save_tokens(tu, filename)

    # Get the contents of the AST text file.
    file_string = open(filename, "r").read()

    # We don't need the file anymore
    with suppress(FileNotFoundError):
        os.remove(filename)

    # Make sure we get the AST we expect.
    assert file_string == '''int <- type = KEYWORD
main <- type = IDENTIFIER
( <- type = PUNCTUATION
int <- type = KEYWORD
x <- type = IDENTIFIER
, <- type = PUNCTUATION
int <- type = KEYWORD
y <- type = IDENTIFIER
) <- type = PUNCTUATION
{ <- type = PUNCTUATION
return <- type = KEYWORD
x <- type = IDENTIFIER
+ <- type = PUNCTUATION
y <- type = IDENTIFIER
} <- type = PUNCTUATION
'''

    
def test_isUnlockCalled(): 

    # Our C++ 'file'
    cpp_file = '''
    class ourType 
    {
        public:
        void lock();
        void unlock();
    };

    int main()
    {
        ourType member1;
        member1.lock();
        ourType member2;
        member2.unlock();
    }
    '''

    # Generate the translation unit from our 'file'.
    idx = clang.cindex.Index.create()
    tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                unsaved_files=[('tmp.cpp', cpp_file)],  options=0)
    cursor = tu.cursor
    
    # Make sure we get that unlock is called
    assert isUnlockCalled(cursor, "member2") == True
    assert isUnlockCalled(cursor,"member3") == False

def test_findCaller():
    
    # Our C++ 'file'
    cpp_file = '''
    class ourType 
    {
        public:
        void lock();
        void unlock();
    };

    int main()
    {
        ourType member1;
        member1.lock();
        ourType member2;
        member2.unlock();
    }
    '''
    # Generate the translation unit from our 'file'.
    idx = clang.cindex.Index.create()
    tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                unsaved_files=[('tmp.cpp', cpp_file)],  options=0)
    cursor = tu.cursor

    # Make sure we get “member1”
    assert findCaller(cursor, "lock") == "member1"

    # try:
        # assert findCaller(cursor, "lock") == "member1"
    # except AssertionError:
    #     print(findCaller(cursor, "lock"))
   


def test_public_mutex_members_API():
    #test public.cpp file
    print("First file - with public mutexes")
    idx = clang.cindex.Index.create()
    tu = idx.parse("public.cpp", args=['-std=c++11'])
    main.traverse(tu.cursor)
    if len(main.cursor_lines) != 0:
        print("Public mutexes found on lines " + main.cursor_lines)
    else:
        print("No public mutexes found")
    assert main.cursor_lines == "15 33 " #there is 2 public mutexes each located in on of the lines of cpp file

    # test public1.cpp file
    print("Second file - without public mutexes")
    main.cursor_lines = ""
    idx1 = clang.cindex.Index.create()
    tu1 = idx1.parse("public1.cpp", args=['-std=c++11'])
    main.traverse(tu1.cursor)
    if len(main.cursor_lines) != 0:
        print("Public mutexes found on lines " + main.cursor_lines)
    else:
        print("No public mutexes found")
    assert main.cursor_lines == "" #no public mutexes so no line number is outputed
