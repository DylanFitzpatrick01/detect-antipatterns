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
  nextAtomicIsCorrect = False
  def __init__(self):
    self.readWritesToCheck = []
    
    self.affected = dict()      # Dict of atomics and lists of affected vars
    self.investagating = list() # Stack of cursors
    self.skipNext = False
    self.possibleAtomicWrite = None
    self.branchLevel = 0        # The level of branches we're in. 0 is none, >1
                                # is a nested branch
    self.endIfReached = False


  # When a var will be changed, add it to the stack. When moved on, remove it
  # If entered method tell it next return

  def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):


    # If we found an if statement, add it to the list
    if cursor.kind == clang.cindex.CursorKind.IF_STMT:
      self.atomic_if_conditions[ConditionBodyStatement(cursor)] = list()
      #FIXME
      print(f"[Line {cursor.extent.start.line}] if stmt cursor ")
      if (cursor.extent.start.line == 93):
        h = list(cursor.get_children())
        
        print("h")
    if (cursor.extent.start.line == 101):
      print("h")

    # Else if self.atomic_if_conditions is not empty     (since self.if_keys = self.atomic_if_conditions.keys())
    elif (self.if_keys):
      # Check if cursor is inside if statement
      if cursor.extent.start.line <= list(self.if_keys)[-1].cursor.extent.end.line:
        # If the cursor belongs to a single check-then-set instruction
        if cursor.spelling == "compare_exchange_strong":
            # Mark the next atomic as being correctly checked then set in a single instruction
            self.nextAtomicIsCorrect = True
            
        # If the cursor is a compound statement '{ }', and we are yet to get the body of the statement
        if cursor.kind == clang.cindex.CursorKind.COMPOUND_STMT and list(self.if_keys)[-1].compound_stmt is None:    
            # Set the body of the statement as being this cursor
             list(self.if_keys)[-1].compound_stmt = cursor
        
        # If we are missing the body of the most recent statement
        if (list(self.if_keys)[-1].compound_stmt is None):
          
          # If the current cursor is of type atomic
          if "std::atomic" in cursor.type.spelling:
            
            # And we haven't marked the next atomic as being correctly checked and set
            if (not self.nextAtomicIsCorrect):
              # Then this atomic belongs to the condition of the most recent statement, so append it to the values of the statement key
              self.atomic_if_conditions[list(self.if_keys)[-1]].append(cursor)
            
            # Otherwise if we have marked the next atomic as being correctly checked and set
            else:
              # Don't do anything with the current atomic (cursor), and reset the boolean marker for the next atomic
              self.nextAtomicIsCorrect = False

        # If we are not missing the body of the most recent statement
        else:

          # Check if the current cursor belongs to an atomic write
          if (self.possibleAtomicWrite):

            newAlert = Alert(cursor.translation_unit, self.possibleAtomicWrite[0].cursor.extent,
                f"Read and write detected instead of using compare_exchange_strong on lines [{self.possibleAtomicWrite[0].cursor.extent.start.line} -> " +
                f"{self.possibleAtomicWrite[1].extent.end.line}]\n" +
                f"We suggest you use {self.possibleAtomicWrite[1].displayname}.compare_exchange_strong(),\n" +
                f"as this read and write is non-atomical.", "error")

            #TODO FIX LIMITED CHECKING CAPABILITY
            # Check if cursor is a write
            if (cursor.kind == clang.cindex.CursorKind.CXX_BOOL_LITERAL_EXPR):
              #if newAlert not in alerts:
              alerts.append(newAlert)

            elif cursor.type.spelling in self.possibleAtomicWrite[1].type.spelling and (cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR or cursor.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR):
              #if newAlert not in alerts:
              alerts.append(newAlert)
            # TODO: Check if operator is always before the values written with?
            if not "operator" in cursor.displayname:
              self.possibleAtomicWrite = None

          if "std::atomic" in cursor.type.spelling:
            if (not self.nextAtomicIsCorrect):
              # TODO: Work for parent if stmt conditions too.. but try not to make multiple alerts for one incident
              for statement in list(self.atomic_if_conditions):
                if (statement.compound_stmt):
                  print(f"stmt check {statement.compound_stmt.extent.start.line}")
                  if (statement.compound_end >= cursor.extent.end.line):
                    for atomic_condition in self.atomic_if_conditions[statement]:
                        if atomic_condition.referenced.get_usr() == cursor.referenced.get_usr():
                          self.possibleAtomicWrite = (statement, cursor)
                  else:
                    print(f"Deleting stmt on Line: {statement.cursor.extent.start.line}, as this cursor is on Line: {cursor.extent.start.line}")
                    del self.atomic_if_conditions[statement]
                else:
                  print(f"{statement.cursor.extent.start.line} doesn't have a compound statement")
            else:
              self.nextAtomicIsCorrect = False
          
      
      else:
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