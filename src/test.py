import main, os, importlib.util, clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import FormalCheckInterface

# --------UNIT TESTS------- #

# TODO add test for calling out of locked scope
# TODO add test for lock order

def test_locked_call():
	if (not os.path.isabs("../cpp_tests/already_locked.cpp")):
		abs_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../cpp_tests/already_locked.cpp"))

	alerts = run_check_on_file("../Checks/alreadyLocked.py", "../cpp_tests/already_locked.cpp")

	messages = list()
	for alert in alerts:
		messages.append(alert.message)

	expected = list()
	expected.append(
		"Called test from a locked scope.\n" + 
		"  a is locked in: " + abs_file_path + " at line: 18"
	)

	expected.append(
		"Called test from a locked scope.\n" + 
		"  c is locked in: " + abs_file_path + " at line: 30"
	)

	expected.append(
		"Called test from a locked scope.\n" + 
		"  d is locked in: " + abs_file_path + " at line: 36"
	)
		
	for message in messages:
		assert message in expected
	
	for message in expected:
		assert message in messages

def test_already_locked():
	if (not os.path.isabs("../cpp_tests/already_locked.cpp")):
		abs_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../cpp_tests/already_locked.cpp"))

	alerts = run_check_on_file("../Checks/alreadyLocked.py", "../cpp_tests/already_locked.cpp")

	messages = list()

	for alert in alerts:
		messages.append(alert.message)

	expected = list()
	expected.append("a might already be locked\n" + "  a is locked in: " + abs_file_path + " at line: 27")
	expected.append("b might already be locked\n" + "  b is locked in: " + abs_file_path + " at line: 38")
	expected.append("c might already be locked\n" + "  c is locked in: " + abs_file_path + " at line: 43")
	expected.append("d might already be locked\n" + "  d is locked in: " + abs_file_path + " at line: 48")


	for message in messages:
		assert message in expected
	
	for message in expected:
		assert message in messages

def test_lock_order():
	if (not os.path.isabs("../cpp_tests/lock_order.cpp")):
		abs_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../cpp_tests/lock_order.cpp"))

	alerts = run_check_on_file("../Checks/lockOrder.py", "../cpp_tests/lock_order.cpp")
	messages = list()

	for alert in alerts:
		messages.append(alert.message)

	expected = list()
	expected.append(
		"Locking order may cause deadlock.\n" + 
		"Locked: b in: " + abs_file_path + " at line: 12\n" +
		"Locked: a in: " + abs_file_path + " at line: 13\n" +
		"\n" + 
		"Locked: a in: " + abs_file_path + " at line: 49\n" + 
		"Locked: b in: " + abs_file_path + " at line: 50\n")
	expected.append(
		"Locking order may cause deadlock.\n" + 
		"Locked: c in: " + abs_file_path + " at line: 20\n" +
		"Locked: d in: " + abs_file_path + " at line: 21\n" +
		"\n" + 
		"Locked: d in: " + abs_file_path + " at line: 24\n" + 
		"Locked: c in: " + abs_file_path + " at line: 25\n")
	expected.append(
		"Locking order may cause deadlock.\n" + 
		"Locked: e in: " + abs_file_path + " at line: 35\n" +
		"Locked: f in: " + abs_file_path + " at line: 36\n" +
		"\n" + 
		"Locked: f in: " + abs_file_path + " at line: 40\n" + 
		"Locked: e in: " + abs_file_path + " at line: 42\n")
	
	for message in messages:
		assert message in expected
	
	for message in expected:
		assert message in messages

def test_locked_call():
	if (not os.path.isabs("../cpp_tests/called_out_of_locked_scope.cpp")):
		abs_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../cpp_tests/called_out_of_locked_scope.cpp"))

	alerts = run_check_on_file("../Checks/calledOutOfLockedScope.py", "../cpp_tests/called_out_of_locked_scope.cpp")
	messages = list()

	for alert in alerts:
		messages.append(alert.message)

	expected = list()
	expected.append(
		"Called: test from a locked scope.\n" +
		"  a is locked in: " + abs_file_path + " at line: 18"
	)
	expected.append(
		"Called: test from a locked scope.\n" +
		"  c is locked in: " + abs_file_path + " at line: 30"
	)
	expected.append(
		"Called: test from a locked scope.\n" +
		"  d is locked in: " + abs_file_path + " at line: 36"
	)

	for message in messages:
		assert message in expected
	
	for message in expected:
		assert message in messages

# Unit test for manualLockUnlock.py
def test_manual_lock_unlock():

	# Check a file with manual locks.
	alerts: List[Alert] = run_check_on_file("../Checks/manualLockUnlock.py", "../cpp_tests/public.cpp")
	# assert alerts[0].message == ("A manual lock is used in this scope without an unlock!.\n" +
	#                              "Please either replace 'mDataAccess.lock();' with 'std::lock_guard<std::mutex> lock(mDataAccess);' (RECCOMMENDED),\n" +
	#                              "or add 'mDataAccess.unlock();' at the end of this critical section.")
	
	assert alerts[0].message == "mDataAccess1 is locked/unlocked manually, RAII is recommended"

	assert alerts[1].message == "It is possible that mDataAccess1 is not unlocked before leaving scope"

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


# Unit test for member_locked_in_some_methods.py
def test_member_locked_in_some_methods():
	# Check files with data members that may be locked in some, but not all methods
	# This checks both files that have data members locked in some methods, and files that should pass so there are no false positives.
	
	# ERROR DETECTION TESTS
	alerts: List[Alert] = run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/error_in_method_scope_locks.cpp")
	alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/error_in_method_scope.cpp"))
	alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/error_in_method_with_nested_scopes.cpp"))
	assert alerts[0].message == ("Data member 'mState' at (line: 34, column: 39) is not accessed with a lock_guard or lock/unlock combination in this method, \nbut is accessed with a lock_guard or lock/unlock combination in other methods\n Are you missing a lock_guard or lock/unlock combination before 'mState'?")
	assert alerts[1].message == ("Data member 'mState' at (line: 32, column: 39) is not accessed with a lock_guard or lock/unlock combination in this method, \nbut is accessed with a lock_guard or lock/unlock combination in other methods\n Are you missing a lock_guard or lock/unlock combination before 'mState'?")
	assert alerts[2].message == ("Data member 'mState' at (line: 43, column: 59) is not accessed with a lock_guard or lock/unlock combination in this method, \nbut is accessed with a lock_guard or lock/unlock combination in other methods\n Are you missing a lock_guard or lock/unlock combination before 'mState'?")
	
	
	# PASS DETECTION TESTS
	alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/pass_in_method_scope_locks.cpp"))
	alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/pass_in_method_scope.cpp"))
	alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/pass_in_method_with_nested_scopes_locks.cpp"))
	alerts.extend(run_check_on_file("../Checks/member_locked_in_some_methods.py", "../cpp_tests/member_locked_in_some_methods/pass_in_method_scope.cpp"))
	
	# We know that there should be exactly 3 alerts from the error detection tests, so if that remains at 3 after the pass detection tests,
	# No errors were detected in the passes (as it should be in a pass)
	assert len(alerts) == 3


def test_immutable_object():
	
	# Run our check on a file that'll trigger an alert!
	alerts: List[Alert] = run_check_on_file("../Checks/immutableObjects.py", "../cpp_tests/immutable.cpp")
	assert alerts[0].message == "71.0% of Variables are constant. This may cause an immutable object error"
	
	# Run our check on a file that won't return any alerts.
	alerts = run_check_on_file("../Checks/immutableObjects.py", "../cpp_tests/public.cpp")
	assert len(alerts) == 0


def test_atomic_check_and_set():
    # ERROR TESTS:
    alerts: List[Alert] = run_check_on_file("../Checks/check_and_set_atomics.py", "../cpp_tests/atomic_branching.cpp")
    assert len(alerts) == 5
    assert alerts[0].message == 'Read and write detected instead of using compare_exchange_strong on lines [45 -> 47]\nWe suggest you use mIsSet.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[1].message == 'Read and write detected instead of using compare_exchange_strong on lines [54 -> 56]\nWe suggest you use mIsSet.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[2].message == 'Read and write detected instead of using compare_exchange_strong on lines [63 -> 65]\nWe suggest you use mIsSet.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[3].message == 'Read and write detected instead of using compare_exchange_strong on lines [74 -> 75]\nWe suggest you use mIsSet2.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[4].message == 'Read and write detected instead of using compare_exchange_strong on lines [86 -> 88]\nWe suggest you use mIsSet.compare_exchange_strong(),\nas this read and write is non-atomical.'
    alerts: List[Alert] = run_check_on_file("../Checks/check_and_set_atomics.py", "../cpp_tests/atomic_check_and_set_nested_err.cpp")
    assert len(alerts) == 3
    assert alerts[0].message == 'Read and write detected instead of using compare_exchange_strong on lines [66 -> 70]\nWe suggest you use mIsSet2.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[1].message == 'Read and write detected instead of using compare_exchange_strong on lines [97 -> 100]\nWe suggest you use mIsSet.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[2].message == 'Read and write detected instead of using compare_exchange_strong on lines [97 -> 108]\nWe suggest you use mIsSet.compare_exchange_strong(),\nas this read and write is non-atomical.'

    alerts: List[Alert] = run_check_on_file("../Checks/check_and_set_atomics.py", "../cpp_tests/atomic_check_and_set_nested_err2.cpp")
    assert len(alerts) == 4
    assert alerts[0].message == 'Read and write detected instead of using compare_exchange_strong on lines [27 -> 29]\nWe suggest you use mIsSet.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[1].message == 'Read and write detected instead of using compare_exchange_strong on lines [32 -> 34]\nWe suggest you use mIsSet2.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[2].message == 'Read and write detected instead of using compare_exchange_strong on lines [114 -> 118]\nWe suggest you use mIsSet2.compare_exchange_strong(),\nas this read and write is non-atomical.'
    assert alerts[3].message == 'Read and write detected instead of using compare_exchange_strong on lines [111 -> 112]\nWe suggest you use mIsSet.compare_exchange_strong(),\nas this read and write is non-atomical.'
    

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
	alerts = list()
	main.traverse(tu.cursor, check_list, alerts, list())

	return alerts

#FIXME
if __name__ == "__main__":
    test_atomic_check_and_set()
