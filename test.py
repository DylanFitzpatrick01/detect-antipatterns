import clang.cindex
from main import *
from contextlib import suppress
from observer import *
from member_locked_in_some_methods import *
import os

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
    save_tokens(tu, filename)

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

def test_count_tokens():

    # Our C++ 'file'
    cpp_file = '''
    int main(x, y)
    {
        return x + y
    }
    '''

    # Generate the translation unit from our 'file'.
    idx = clang.cindex.Index.create()
    tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                unsaved_files=[('tmp.cpp', cpp_file)],  options=0)
    
    # Make sure we get the number of tokens we expect.
    assert count_tokens(tu) == 13

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
    
    
    searchNodes(eventSrc=eventSrc, file_path="lock_in_some_methods.cpp")
    correct_output = """Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file 'lock_in_some_methods.cpp', line 17, column 38>
Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file 'lock_in_some_methods.cpp', line 24, column 38>
Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file 'lock_in_some_methods.cpp', line 36, column 16>
Detected a 'std::lock_guard<std::mutex>' Lockguard's Name: 'lock_guard' at <SourceLocation file 'lock_in_some_methods.cpp', line 17, column 33>
Detected a 'std::lock_guard<std::mutex>' Lockguard's Name: 'lock_guard' at <SourceLocation file 'lock_in_some_methods.cpp', line 24, column 33>
Detected variable std::string: 'mState' at <SourceLocation file 'lock_in_some_methods.cpp', line 35, column 17>
Detected variable std::mutex: 'mDataAccess' at <SourceLocation file 'lock_in_some_methods.cpp', line 36, column 16>
Class 'MyClass' found at <SourceLocation file 'lock_in_some_methods.cpp', line 5, column 7>
Method 'getState()' found at <SourceLocation file 'lock_in_some_methods.cpp', line 15, column 13>
Method 'updateState(const std::string &)' found at <SourceLocation file 'lock_in_some_methods.cpp', line 22, column 6>
Method 'logState()' found at <SourceLocation file 'lock_in_some_methods.cpp', line 29, column 6>\n"""
    output_str = mutex_observer.output + lock_guard_observer.output + declared_variable_observer.output + class_observer.output + function_observer.output
    assert(output_str) == correct_output
    
if __name__ == "__main__":
    test_observers()
    