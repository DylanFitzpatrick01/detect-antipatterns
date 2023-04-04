from formalCheckInterface import FormalCheckInterface
from alerts import Alert
import clang.cindex
from Util import ConditionBodyStatement

# TODO: Add handling for nested if stmts
# TODO: Add test files for nested if stmts
# TODO: Add handling for multi-lined if conditions
class Check(FormalCheckInterface):
  atomic_if_conditions = dict()        # Key - If statement cursor, Value - List of cursors in the if condition
  if_keys = atomic_if_conditions.keys()  # The keys of atomic_if_conditions, so we can get the most recent if statement using [-1] indexing
  currentAtomic = None
  nextAtomicIsCorrect = False
  def __init__(self):
    
    self.affected = dict()      # Dict of atomics and lists of affected vars
    self.investagating = list() # Stack of cursors
    self.skipNext = False
    self.atomicWrite = False
    self.branchLevel = 0        # The level of branches we're in. 0 is none, >1
                                # is a nested branch
    self.endIfReached = False
    

  # When a var will be changed, add it to the stack. When moved on, remove it
  # If entered method tell it next return


# TODO:
# If we enter an if-else body and change the value of an atomic whose value affected the condition.


  def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
    
    
    
    #print(f"<line {cursor.extent.start.line} column {cursor.extent.start.column} => line {cursor.extent.end.line} column {cursor.extent.end.line}>  {cursor.type.spelling} '{cursor.displayname}' {cursor.kind}")
    # If we found an if statement, add it to the list
    if cursor.kind == clang.cindex.CursorKind.IF_STMT:
      self.atomic_if_conditions[cursor] = list()
      self.atomic_if_conditions[ConditionBodyStatement(cursor)]
      print("if stmt cursor")
      
    # Else if self.atomic_if_conditions is not empty     (since self.if_keys = self.atomic_if_conditions.keys())
    elif (self.if_keys):
      # Check if cursor is inside if statement
      if cursor.extent.start.line <= list(self.if_keys)[-1].extent.end.line:
        # Check if cursor is inside condition of if statement
        if (cursor.extent.start.line == list(self.if_keys)[-1].extent.start.line):
          if "std::atomic" in cursor.type.spelling:
            self.atomic_if_conditions[list(self.if_keys)[-1]].append(cursor)
        if cursor.spelling == "compare_exchange_strong":
            self.nextAtomicIsCorrect = True

        if "std::atomic" in cursor.type.spelling:
          if (not self.nextAtomicIsCorrect) and any((condition_cursor.referenced.get_usr() == cursor.referenced.get_usr()) for condition_cursor in self.atomic_if_conditions[list(self.if_keys)[-1]]):
            self.currentAtomic = cursor
          else:
            self.nextAtomicIsCorrect = False
          if cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
            if cursor.referenced.get_usr() in self.affected:
              self.affected[cursor.referenced.get_usr()].append(cursor)
            else:
              self.affected[cursor.referenced.get_usr()] = [cursor]
          elif cursor.kind == clang.cindex.CursorKind.FIELD_DECL:
            self.affected[cursor.get_usr()] = list()
        elif (self.currentAtomic):
          if (self.currentAtomic.extent.start.line == cursor.extent.start.line):
            newAlert = Alert(cursor.translation_unit, list(self.if_keys)[-1].extent,
                f"Read and write detected instead of using compare_exchange_strong\n " +
                f"We suggest you use {self.currentAtomic.displayname}.compare_exchange_strong(),\n " +
                f"as this read and write is non-atomical.", "error")
            # Check if cursor is a write
            if (cursor.kind == clang.cindex.CursorKind.CXX_BOOL_LITERAL_EXPR):
              if newAlert not in alerts:
                alerts.append(newAlert)
            elif (cursor.type.spelling in self.currentAtomic.type.spelling and cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR):
              if newAlert not in alerts:
                alerts.append(newAlert)
          else:
            self.currentAtomic = None
      
      else:
        self.currentAtomic = None
        del self.atomic_if_conditions[list(self.if_keys)[-1]]
      

  def scope_increased(self, alerts):
    self.branchLevel += 1

  def scope_decreased(self, alerts):
    self.branchLevel -= 1

#  def getStmts(self):
#    for name in dir(clang.cindex.CursorKind):
#      if name.endswith("STMT"):
#          print(getattr(clang.cindex.CursorKind, name))
#          
#if __name__ == "__main__":
#  Check.getStmts()