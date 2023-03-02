import clang.cindex
from main import *
from contextlib import suppress
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

		# Generate the translation unit from our 'file'.
		idx = clang.cindex.Index.create()
		tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
								unsaved_files=[('tmp.cpp', cpp_file)],  options=0)
		
		# Make sure we get the number of tokens we expect.
		assert count_tokens(tu) == 13

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
	out = run_checks("cpp_tests/manual_detection_0.cpp", True, False)
	
	expected = ["Manual locking in file: cpp_tests/manual_detection_0.cpp at line: 9\n	RAII is preferred",
							"Manual locking in file: cpp_tests/manual_detection_0.cpp at line: 13\n	RAII is preferred",
							"Manual unlocking in file: cpp_tests/manual_detection_0.cpp at line: 18\n	RAII is preferred",  
							"Manual unlocking in file: cpp_tests/manual_detection_0.cpp at line: 21\n	RAII is preferred",   
							"Manual unlocking in file: cpp_tests/manual_detection_0.cpp at line: 25\n	RAII is preferred"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

	#Test that locking in other functions is detected correctly
	out = run_checks("cpp_tests/manual_detection_1.cpp", True, False)

	expected = ["Manual locking in file: cpp_tests/manual_detection_1.cpp at line: 9\n	RAII is preferred",
							 "Manual locking in file: cpp_tests/manual_detection_1.cpp at line: 10\n	RAII is preferred",
							 "Manual unlocking in file: cpp_tests/manual_detection_1.cpp at line: 14\n	RAII is preferred",
							 "Manual unlocking in file: cpp_tests/manual_detection_1.cpp at line: 17\n	RAII is preferred",
							 "Manual locking in file: cpp_tests/manual_detection_1.cpp at line: 28\n	RAII is preferred"
	]
	
	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

#Leon Byrne
def test_calling_out_of_locked_scope():
	out = run_checks("cpp_tests/calling_out_of_locked_scope_0.cpp", False, True)

	expected = ["Called: test1 from a locked scope in file: cpp_tests/calling_out_of_locked_scope_0.cpp at line: 16",
							"Called: test1 from a locked scope in file: cpp_tests/calling_out_of_locked_scope_0.cpp at line: 29",
							"Called: test1 from a locked scope in file: cpp_tests/calling_out_of_locked_scope_0.cpp at line: 35"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected


	out = run_checks("cpp_tests/calling_out_of_locked_scope_1.cpp", False, True)

	expected = ["Called: test from a locked scope in file: cpp_tests/calling_out_of_locked_scope_1.cpp at line: 27"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

	#Testing called to a classes methods while locked
	#Allowed by the clients example
	out = run_checks("cpp_tests/calling_out_of_locked_scope_1.cpp", False, True)

	expected = ["Called: test from a locked scope in file: cpp_tests/calling_out_of_locked_scope_1.cpp at line: 27"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected
