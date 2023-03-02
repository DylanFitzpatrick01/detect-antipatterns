from locks import *

def test0():
	out = tests("cpp_tests/calling_out_of_locked_scope_0.cpp", False, True)

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

def test1():
	out = tests("cpp_tests/calling_out_of_locked_scope_1.cpp", False, True)

	expected = ["Called: test from a locked scope in file: cpp_tests/calling_out_of_locked_scope_1.cpp at line: 27"
	]

	#Doesn't matter the order, only that all are in the output from tests()
	for str in expected:
		assert str in out

	#But we need to make sure that all predicted are present and all present were predicted
	for str in out:
		assert str in expected