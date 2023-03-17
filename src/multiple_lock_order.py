import clang.cindex
from observer import *
from scope import *
import inspect
import re

multiMutexEventSource = EventSource()
multiMutexObserver = tagObserver("std::lock_guard<std::mutex>")
multiMutexEventSource.addObserver(multiMutexObserver)

#Liam Byrne
#Checks the order in which locks are first called
#If the order changes later in the code, error is flagged
def check_lock_order_conflict(multi_order):
	heldLocks = list()
	usedLocks = list()
	highestIndex = 0
	error_message = ""
	order_flag = 0
	for mutex in multi_order:
		if mutex in heldLocks:
			if mutex in usedLocks:
				usedLocks.clear()
				highestIndex = 0
			usedLocks.append(mutex)
			if (heldLocks.index(mutex) >= highestIndex):
				highestIndex = heldLocks.index(mutex)
			else:
				order_flag = 1
				error_message = error_message + "Error!: mutex " + str(mutex) + " is in the incorrect order!\n"
		else:
			heldLocks.append(mutex)
	if order_flag == 0:
		error_message = "No lock order errors detected!"
	return error_message

def multi_lock_test(file_selected):
    with open(file_selected, 'r') as file:
        contents = file.read()
	
    matches = re.findall(r'std::lock_guard<std::mutex>\s+lock\((\w+)\);', contents)
    mutex_names = []
    for match in matches:
        mutex_names.append(match)
    multi_order = list(mutex_names)
    
    error_message = check_lock_order_conflict(multi_order)
    print(error_message)
    return error_message

if __name__ == "__main__":
	multi_lock_test("cpp_tests/multiple_locks_order.cpp")