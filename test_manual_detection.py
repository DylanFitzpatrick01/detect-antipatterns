from locks import *

def test0():
	#Testing that nestling in if statements doesn't interfere
	out = tests("cpp_tests/manual_detection_0.cpp", True, False)
	
	expected = ["Manual locking in file: cpp_tests/manual_detection_0.cpp at line: 9\n  RAII is preferred",
	  					"Manual locking in file: cpp_tests/manual_detection_0.cpp at line: 13\n  RAII is preferred",
						  "Manual unlocking in file: cpp_tests/manual_detection_0.cpp at line: 18\n  RAII is preferred",  
						  "Manual unlocking in file: cpp_tests/manual_detection_0.cpp at line: 21\n  RAII is preferred",   
						  "Manual unlocking in file: cpp_tests/manual_detection_0.cpp at line: 25\n  RAII is preferred"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

def test1():
	out = tests("cpp_tests/manual_detection_1.cpp", True, False)

	expected = ["Manual locking in file: cpp_tests/manual_detection_1.cpp at line: 9\n  RAII is preferred",
	     				"Manual locking in file: cpp_tests/manual_detection_1.cpp at line: 10\n  RAII is preferred",
	     				"Manual unlocking in file: cpp_tests/manual_detection_1.cpp at line: 14\n  RAII is preferred",
	     				"Manual unlocking in file: cpp_tests/manual_detection_1.cpp at line: 17\n  RAII is preferred",
	     				"Manual locking in file: cpp_tests/manual_detection_1.cpp at line: 28\n  RAII is preferred"
	]
	
	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected

def test2():
	out = tests("cpp_tests/manual_dection_2.cpp", True, False)

	#Want to check that there are no errors
	#Out should be empty
	assert not out