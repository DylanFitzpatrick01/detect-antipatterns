import clang.cindex
import main
from contextlib import suppress
from missingUnlock import findCaller, isUnlockCalled
from observer import *
from member_locked_in_some_methods import *
from multiple_lock_order import *
import os
import pytest

from locks import *

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
		assert main.count_tokens(tu) == 13

		# Generate the translation unit from our 'file'.
		idx = clang.cindex.Index.create()
		tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
								unsaved_files=[('tmp.cpp', cpp_file)],  options=0)
		
		# Make sure we get the number of tokens we expect.
		assert main.count_tokens(tu) == 13

def test_public_mutex_members_API():
    #test public.cpp file
    print("First file - with public mutexes")
    idx = clang.cindex.Index.create()
    tu = idx.parse("../cpp_tests/public.cpp", args=['-std=c++11'])
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
    tu1 = idx1.parse("../cpp_tests/public1.cpp", args=['-std=c++11'])
    main.traverse(tu1.cursor)
    if len(main.cursor_lines) != 0:
        print("Public mutexes found on lines " + main.cursor_lines)
    else:
        print("No public mutexes found")
    assert main.cursor_lines == "" #no public mutexes so no line number is outputed

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
    
    
    searchNodes(eventSrc=eventSrc, file_path="../cpp_tests/locked_member_in_some_err.cpp")
    
    correct_output = f"""Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 17, column 38>
Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 24, column 38>
Detected a 'std::mutex', Name: 'mDataAccess' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 37, column 16>
Detected a 'std::lock_guard<std::mutex>' Lockguard's Name: 'lock_guard' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 17, column 33>
Detected a 'std::lock_guard<std::mutex>' Lockguard's Name: 'lock_guard' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 24, column 33>
Detected variable std::string: 'mState' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 36, column 17>
Detected variable std::mutex: 'mDataAccess' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 37, column 16>
Detected variable MyClass: 'MyClass' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 5, column 7>
Detected variable std::string (): 'getState()' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 15, column 13>
Detected variable void (const std::string &): 'updateState(const std::string &)' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 22, column 6>
Detected variable void (): 'logState()' at <SourceLocation file '../cpp_tests/locked_member_in_some_err.cpp', line 29, column 6>
"""
    
    output_str = f"{mutex_observer.output}{lock_guard_observer.output}{declared_variable_observer.output}{class_observer.output}{function_observer.output}"
    assert(output_str) == correct_output


# Gráinne Ready
def test_member_locked_in_some_methods():
    correct_error_output = """Data member 'mState' is accessed without a lock_guard in this method,
but is accessed with a lock_guard in other methods
 Are you missing a lock_guard before 'mState'?"""
    correct_pass_output = "PASSED - For data members locked in some but not all methods"
    error_output = checkIfMembersLockedInSomeMethods("../cpp_tests/locked_member_in_some_err.cpp")
    pass_output = checkIfMembersLockedInSomeMethods("../cpp_tests/locked_member_in_some_pass.cpp")
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
	 
#Leon Byrne
def test_manual_detection():
		#Testing that nestling in if statements doesn't interfere
	out = run_checks("../cpp_tests/manual_detection_0.cpp", True, False)
	
	expected = ["Manual locking in file: ../cpp_tests/manual_detection_0.cpp at line: 9\n	RAII is preferred",
							"Manual locking in file: ../cpp_tests/manual_detection_0.cpp at line: 13\n	RAII is preferred",
							"Manual unlocking in file: ../cpp_tests/manual_detection_0.cpp at line: 18\n	RAII is preferred",  
							"Manual unlocking in file: ../cpp_tests/manual_detection_0.cpp at line: 21\n	RAII is preferred",   
							"Manual unlocking in file: ../cpp_tests/manual_detection_0.cpp at line: 25\n	RAII is preferred"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

	#Test that locking in other functions is detected correctly
	out = run_checks("../cpp_tests/manual_detection_1.cpp", True, False)

	expected = ["Manual locking in file: ../cpp_tests/manual_detection_1.cpp at line: 9\n	RAII is preferred",
							 "Manual locking in file: ../cpp_tests/manual_detection_1.cpp at line: 10\n	RAII is preferred",
							 "Manual unlocking in file: ../cpp_tests/manual_detection_1.cpp at line: 14\n	RAII is preferred",
							 "Manual unlocking in file: ../cpp_tests/manual_detection_1.cpp at line: 17\n	RAII is preferred",
							 "Manual locking in file: ../cpp_tests/manual_detection_1.cpp at line: 28\n	RAII is preferred"
	]
	
	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

#Leon Byrne
def test_calling_out_of_locked_scope():
	out = run_checks("../cpp_tests/calling_out_of_locked_scope_0.cpp", False, True)

	expected = ["Called: test1 from a locked scope in file: ../cpp_tests/calling_out_of_locked_scope_0.cpp at line: 16",
							"Called: test1 from a locked scope in file: ../cpp_tests/calling_out_of_locked_scope_0.cpp at line: 29",
							"Called: test1 from a locked scope in file: ../cpp_tests/calling_out_of_locked_scope_0.cpp at line: 35"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected


	out = run_checks("../cpp_tests/calling_out_of_locked_scope_1.cpp", False, True)

	expected = ["Called: test from a locked scope in file: ../cpp_tests/calling_out_of_locked_scope_1.cpp at line: 27"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

	#Testing called to a classes methods while locked
	#Allowed by the clients example
	out = run_checks("../cpp_tests/calling_out_of_locked_scope_1.cpp", False, True)

	expected = ["Called: test from a locked scope in file: ../cpp_tests/calling_out_of_locked_scope_1.cpp at line: 27"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

def test_multiple_lock_order():
	result = multi_lock_test("../cpp_tests/multiple_locks_order.cpp")

	expected = ["Error!: mutex mMutex1 is in the incorrect order!\n"]

	for str in expected:
		assert str in result

	for str in result:
		assert str in expected

	result = multi_lock_test("../cpp_tests/unlock.cpp")

	expected = ["No lock order errors detected!"]

	for str in expected:
		assert str in result

	for str in result:
		assert str in expected