import clang.cindex
import main
from contextlib import suppress
from missingUnlock import findCaller, isUnlockCalled
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

# Gráinne Ready
def test_observers():
    eventSrc = EventSource()
    eventSrc2 = EventSource()
    mutex_observer = tagObserver("std::mutex")
    lock_guard_observer = tagObserver("std::lock_guard<std::mutex>")
    declared_variable_observer = cursorKindObserver(clang.cindex.CursorKind.FIELD_DECL)
    class_observer = cursorKindObserver(clang.cindex.CursorKind.CLASS_DECL)
    function_observer = cursorKindObserver(clang.cindex.CursorKind.CXX_METHOD)
    
    assert(eventSrc.observers) == []
    eventSrc.addMultipleObservers([mutex_observer, lock_guard_observer, declared_variable_observer, class_observer])
    eventSrc.addObserver(function_observer)
    assert(eventSrc.observers) == [mutex_observer, lock_guard_observer, declared_variable_observer, class_observer, function_observer]

    eventSrc2.addMultipleObservers([mutex_observer, lock_guard_observer, class_observer, function_observer])
    eventSrc2.removeMultipleObservers([mutex_observer, lock_guard_observer, class_observer])
    assert(eventSrc2.observers) == [function_observer]
    
    
    searchNodes(eventSrc=eventSrc, file_path="err_lock_in_some_methods.cpp")
    
    correct_output = """Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 17, column 38>
Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 24, column 38>
Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 37, column 16>
Detected a 'std::lock_guard<std::mutex>' Lockguard's Name: 'lock_guard' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 17, column 33>
Detected a 'std::lock_guard<std::mutex>' Lockguard's Name: 'lock_guard' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 24, column 33>
Detected variable std::string: 'mState' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 36, column 17>
Detected variable std::mutex: 'mDataAccess' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 37, column 16>
Detected variable MyClass: 'MyClass' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 5, column 7>
Detected variable std::string (): 'getState()' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 15, column 13>
Detected variable void (const std::string &): 'updateState(const std::string &)' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 22, column 6>
Detected variable void (): 'logState()' at <SourceLocation file 'err_lock_in_some_methods.cpp', line 29, column 6>\n"""
    
    output_str = mutex_observer.output + lock_guard_observer.output + declared_variable_observer.output + class_observer.output + function_observer.output
    assert(output_str) == correct_output


# Gráinne Ready
def test_member_locked_in_some_methods():
    correct_error_output = """Data member 'mState' is accessed without a lock_guard in this method,
but is accessed with a lock_guard in other methods
 Are you missing a lock_guard before 'mState'?"""
    correct_pass_output = "PASSED - For data members locked in some but not all methods"
    error_output = checkIfMembersLockedInSomeMethods("err_lock_in_some_methods.cpp")
    pass_output = checkIfMembersLockedInSomeMethods("pass_lock_in_some_methods.cpp")
    assert(error_output) == correct_error_output
    assert(pass_output) == correct_pass_output
    
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
