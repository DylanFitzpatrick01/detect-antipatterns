import main, os, importlib.util, clang.cindex
from typing import List
from alerts import Alert
from observer import *
from formalCheckInterface import FormalCheckInterface

# --------UNIT TESTS------- #

# Unit test for manualLockUnlock.py
def test_manual_lock_unlock():

    # Check a file with manual locks.
    alerts: List[Alert] = run_check_on_file("../Checks/manualLockUnlock.py", "../cpp_tests/public.cpp")
    assert alerts[0].message == ("A manual lock is used in this scope without an unlock!.\n" +
                                 "Please either replace 'mDataAccess1.lock();' with 'std::lock_guard<std::mutex> lock(mDataAccess1);' (RECCOMMENDED),\n" +
                                 "or add 'mDataAccess1.unlock();' at the end of this critical section.")
    
    # Check a file without them.
    alerts: List[Alert] = run_check_on_file("../Checks/manualLockUnlock.py", "../cpp_tests/immutable.cpp")
    assert len(alerts) == 0

# Unit test for publicMutexMembers.py
def test_public_mutex_members():

    # Check a file with manual locks.
    alerts: List[Alert] = run_check_on_file("../Checks/publicMutexMembers.py", "../cpp_tests/public.cpp")
    print(alerts[0].message)
    print(alerts[1].message)

    assert alerts[0].message == ("Are you sure you want to have a public mutex called 'mDataAccess1'?\n" +
                                 "Consider making this mutex private.")
    assert alerts[1].message == ("Are you sure you want to have a public mutex called 'mDataAccess5'?\n" +
                                 "Consider making this mutex private.")
    assert len(alerts) == 2
    
    # Check a file without them.
    alerts: List[Alert] = run_check_on_file("../Checks/manualLockUnlock.py", "../cpp_tests/immutable.cpp")
    assert len(alerts) == 0

# Unit test for observers which are used in some antipatterns
def test_observers():
    eventSrc = EventSource()
    eventSrc2 = EventSource()
    mutex_observer = tagObserver("std::mutex")
    lock_guard_observer = tagObserver("std::lock_guard<std::mutex>")
    declared_variable_observer = cursorKindObserver(clang.cindex.CursorKind.FIELD_DECL)
    class_observer = cursorKindObserver(clang.cindex.CursorKind.CLASS_DECL)
    function_observer = cursorKindObserver(clang.cindex.CursorKind.CXX_METHOD)
    record_observer = cursorTypeKindObserver(clang.cindex.TypeKind.RECORD)
    
    assert(eventSrc.observers) == []
    eventSrc.addMultipleObservers([mutex_observer, lock_guard_observer, declared_variable_observer, class_observer, record_observer])
    eventSrc.addObserver(function_observer)
    assert(eventSrc.observers) == [mutex_observer, lock_guard_observer, declared_variable_observer, class_observer, record_observer, function_observer]

    eventSrc2.addMultipleObservers([mutex_observer, lock_guard_observer, class_observer, function_observer])
    eventSrc2.removeMultipleObservers([mutex_observer, lock_guard_observer, class_observer])
    assert(eventSrc2.observers) == [function_observer]
    
    
    searchNodes(eventSrc=eventSrc, file_path="../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp")
    
    correct_output = """Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 17, column 38>
Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 24, column 38>
Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 37, column 16>
Detected a 'std::lock_guard<std::mutex>' Lockguard's Name: 'lock_guard' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 17, column 33>
Detected a 'std::lock_guard<std::mutex>' Lockguard's Name: 'lock_guard' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 24, column 33>
Detected std::string: 'mState' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 36, column 17>
Detected std::mutex: 'mDataAccess' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 37, column 16>
Detected MyClass: 'MyClass' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 5, column 7>
Detected MyClass: 'MyClass' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 5, column 7>
Detected std::mutex: 'class std::mutex' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 17, column 26>
Detected const std::basic_string<char>: 'mState' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 19, column 12>
Detected std::mutex: 'class std::mutex' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 24, column 26>
Detected std::basic_string<char>: 'operator=' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 26, column 5>\nDetected std::mutex: 'class std::mutex' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 37, column 10>
Detected std::string (): 'getState()' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 15, column 13>
Detected void (const std::string &): 'updateState(const std::string &)' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 22, column 6>
Detected void (): 'logState()' at <SourceLocation file '../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp', line 29, column 6>
"""

    output_str = f"{mutex_observer.output}{lock_guard_observer.output}{declared_variable_observer.output}{class_observer.output}{record_observer.output}{function_observer.output}"
    assert(output_str) == correct_output


# Unit test for member_locked_in_some_methods.py
def test_member_locked_in_some_methods():
    # Check files with data members that may be locked in some, but not all methods
    # This checks both files that have data members locked in some methods, and files that should pass so there are no false positives.
    
    # ERROR DETECTION TESTS
    alerts: List[Alert] = run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/error_in_method_scope_locks.cpp")
    alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp"))
    alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/error_in_method_with_nested_scopes.cpp"))
    assert alerts[0].message == ("Data member 'mState' at (line: 34, column: 39) is not accessed with a lock_guard or lock/unlock combination in this method, \nbut is accessed with a lock_guard or lock/unlock combination in other methods\n Are you missing a lock_guard before 'mState'?")
    assert alerts[1].message == ("Data member 'mState' at (line: 32, column: 39) is not accessed with a lock_guard or lock/unlock combination in this method, \nbut is accessed with a lock_guard or lock/unlock combination in other methods\n Are you missing a lock_guard before 'mState'?")
    assert alerts[2].message == ("Data member 'mState' at (line: 43, column: 59) is not accessed with a lock_guard or lock/unlock combination in this method, \nbut is accessed with a lock_guard or lock/unlock combination in other methods\n Are you missing a lock_guard before 'mState'?")
    
    
    # PASS DETECTION TESTS
    alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/pass_in_method_scope_locks.cpp"))
    alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/pass_in_method_scope.cpp"))
    alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/pass_in_method_with_nested_scopes_locks.cpp"))
    alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/pass_in_method_scope.cpp"))
    
    # We know that there should be exactly 3 alerts from the error detection tests, so if that remains at 3 after the pass detection tests,
    # No errors were detected in the passes (as it should be in a pass)
    assert len(alerts) == 3
# --------FUNCTIONS-------- #

def run_check_on_file(check_path: str, file_path: str = None) -> List[Alert]:
    
    # Convert any relative paths to absolute.
    if (not os.path.isabs(file_path)):
        abs_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_path))
    if (not os.path.isabs(check_path)):
        abs_check_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), check_path))
    
    # Get our check filename, so we can import the check!
    check_filename = os.path.basename(check_path)

    # Make sure all of our files exist!
    try:
        open(abs_file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"\nFILE PATH '{file_path}' DOES NOT EXIST")
    try:
        open(abs_check_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"\nCHECK PATH '{check_path}' DOES NOT EXIST")

    # Import the check.
    check_list: List[FormalCheckInterface] = list()
    if (check_filename.endswith(".py")):
        spec = importlib.util.spec_from_file_location(check_filename.removesuffix(".py"), abs_check_path)
        check_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(check_module)
        check_list.append(check_module.Check())

    # Make a Translation Unit
    idx = clang.cindex.Index.create()
    
    tu = idx.parse(abs_file_path)

    # Traverse the AST of the TU, run the check on all cursors,
    # and return all alerts.
    return main.traverse(tu.cursor, check_list)