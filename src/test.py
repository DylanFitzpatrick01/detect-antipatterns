import main, os, importlib.util, clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import FormalCheckInterface

def test_manual_lock_unlock():

    # Check a file with manual locks.
    alerts: List[Alert] = run_check_on_file("../Checks/manualLockUnlock.py", "../cpp_tests/public.cpp")
    assert alerts[0].message == ("A manual lock is used in this scope without an unlock!.\n" +
                                 "Please either replace 'mDataAccess.lock();' with 'std::lock_guard<std::mutex> lock(mDataAccess);' (RECCOMMENDED),\n" +
                                 "or add 'mDataAccess.unlock();' at the end of this critical section.")
    
    # Check a file without them.
    alerts: List[Alert] = run_check_on_file("../Checks/manualLockUnlock.py", "../cpp_tests/immutable.cpp")
    assert len(alerts) == 0


# --------FUNCTIONS-------- #

def run_check_on_file(check_path: str, file_path: str = None) -> List[Alert]:
    
    if (not os.path.isabs(file_path)):
        abs_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_path))
    if (not os.path.isabs(check_path)):
        abs_check_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), check_path))
    test_filename = os.path.basename(check_path)

    try:
        open(abs_file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"\nFILE PATH '{file_path}' DOES NOT EXIST")
    try:
        open(abs_check_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"\nCHECK PATH '{check_path}' DOES NOT EXIST")

    check_list: List[FormalCheckInterface] = list()
    if (test_filename.endswith(".py")):
        spec = importlib.util.spec_from_file_location(test_filename.removesuffix(".py"), abs_check_path)
        check_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(check_module)
        check_list.append(check_module.Check())

    # Make a Translation Unit
    idx = clang.cindex.Index.create()
    tu = idx.parse(abs_file_path, args=['-std=c++11'])

    # Traverse the AST of the TU, run the check on all cursors,
    # and return all alerts.
    return main.traverse(tu.cursor, check_list)