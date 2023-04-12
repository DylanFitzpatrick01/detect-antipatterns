from formalCheckInterface import FormalCheckInterface
from alerts import Alert
import clang.cindex
from Util import ConditionBodyStatement


class Check(FormalCheckInterface):
  statement_kinds = [clang.cindex.CursorKind.IF_STMT, clang.cindex.CursorKind.WHILE_STMT, clang.cindex.CursorKind.DO_STMT, clang.cindex.CursorKind.FOR_STMT]
  statement_dict = dict()        # Key - If statement cursor, Value - List of cursors in the if condition
  statement_keys = statement_dict.keys()  # The keys of statement_dict, so we can get the most recent if statement using [-1] indexing
  nextAtomicIsCorrect = False
  atomic = None
  def __init__(self):
    self.possibleAtomicWrite = None
    self.branchLevel = 0        # The level of branches we're in. 0 is none, >1
                                # is a nested branch

  # When a var will be changed, add it to the stack. When moved on, remove it
  # If entered method tell it next return

  def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
    # If we found a statement, add it to the list
    if cursor.kind in self.statement_kinds:
      self.statement_dict[ConditionBodyStatement(cursor)] = list()
      list(self.statement_keys)[-1].compound_stmt = [child for child in list(cursor.get_children()) if child.kind == clang.cindex.CursorKind.COMPOUND_STMT]

    # Else if self.statement_dict is not empty     (since self.statement_keys = self.statement_dict.keys())
    elif (self.statement_keys):
      # Check if cursor is inside if statement
      if cursor.extent.start.line <= list(self.statement_keys)[-1].cursor.extent.end.line:
        # If the cursor belongs to a single check-then-set instruction
        if "compare_exchange" in cursor.spelling:
            # Mark the next atomic as being correctly checked then set in a single instruction
            self.nextAtomicIsCorrect = True

        # If cursor is inside the most recent statement, but not inside its compound statements..   then its in the condition                                                               
        if (self.isInCondition(cursor, alerts)):
        #  (not any( (cursor.extent.start.line >= compound_stmt.extent.start.line and cursor.extent.start.column >= compound_stmt.extent.start.column) and (cursor.extent.end.line <= compound_stmt.extent.end.line) for compound_stmt in list(self.statement_keys)[-1].compound_stmt)):
          # If the current cursor is of type atomic
          if "std::atomic" in cursor.type.spelling and cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:

            # And we haven't marked the next atomic as being correctly checked and set
            if (not self.nextAtomicIsCorrect):
              # Then this atomic belongs to the condition of the most recent statement, so append it to the values of the statement key
              self.statement_dict[list(self.statement_keys)[-1]].append(cursor)

            # Otherwise if we have marked the next atomic as being correctly checked and set
            else:
              # Don't do anything with the current atomic (cursor), and reset the boolean marker for the next atomic
              self.nextAtomicIsCorrect = False


        else: # If there is a write
          if (self.possibleAtomicWrite):
            # possibleAtomicWrite = ( ConditionBodyStatement, atomic )
            # Create the error message using the possibleAtomicWrite Tuple
            newAlert = Alert(cursor.translation_unit, self.possibleAtomicWrite[0].cursor.extent,
                f"Read and write detected instead of using compare_exchange_strong on lines [{self.possibleAtomicWrite[0].cursor.extent.start.line} -> " +
                f"{self.possibleAtomicWrite[1].extent.end.line}]\n" +
                f"We suggest you use {self.possibleAtomicWrite[1].displayname}.compare_exchange_strong(),\n" +
                f"as this read and write is non-atomical.", "error")
            
            if newAlert not in alerts:
                  alerts.append(newAlert)
                  self.possibleAtomicWrite = None
          
          # These cursor kind if statements are inspired by unsafeAtomics.py, Leon's antipattern.
          if cursor.kind == clang.cindex.CursorKind.CALL_EXPR and "store" in cursor.spelling:               # atomic.store() handling mInt.store(x)
            # Ensure the cursor has children (Error handling)
            if (list(cursor.get_children())):
              # Ensure the cursor has grandchildren (Error handling)
              if (list(list(cursor.get_children())[0].get_children())[0]):
                if "atomic" in list(list(cursor.get_children())[0].get_children())[0].referenced.type.spelling:
                  self.checkConditions(list(list(cursor.get_children())[0].get_children())[0])
          
          elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR and "exchange" in cursor.spelling: # atomic.exchange() handling mInt.exchange(x)
            # Ensure the cursor has children (Error handling)
            if (list(cursor.get_children())):
              # Ensure the cursor has grandchildren (Error handling)
              if (list(list(cursor.get_children())[0].get_children())[0]):
                if "atomic" in list(list(cursor.get_children())[0].get_children())[0].referenced.type.spelling:
                  self.checkConditions(list(list(cursor.get_children())[0].get_children())[0])
          
          elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR and "operator=" in cursor.spelling:  # Generic operator handling for mInt = x
            # Ensure the cursor has children (Error handling)
            if (list(cursor.get_children())):
              # If an atomic is in the first child of the operator=, then we're writing to an atomic
              if "atomic" in list(cursor.get_children())[0].type.spelling:
                self.checkConditions(list(cursor.get_children())[0])
          
          elif cursor.kind == clang.cindex.CursorKind.BINARY_OPERATOR:  # Handling for rare binary operators, mInt = x
            # Ensure the cursor has children (Error handling)
            if (list(cursor.get_children())):
              # If an atomic is in the first child of the binary operator, then we're writing to an atomic
              if "atomic" in list(cursor.get_children())[0].type.spelling:
                self.checkConditions(list(cursor.get_children())[0])

      # If cursor is not inside most recent statement
      else:
        # Dispose of most recent statement
        del self.statement_dict[list(self.statement_keys)[-1]]


  def scope_increased(self, alerts):
    self.branchLevel += 1


  def scope_decreased(self, alerts):
    self.branchLevel -= 1


  def isInCondition(self, cursor, alerts):

    # If cursor is within most recent statement
    if (cursor.extent.start.line >= list(self.statement_keys)[-1].cursor.extent.start.line and \
          cursor.extent.end.line <= list(self.statement_keys)[-1].cursor.extent.end.line):
      # Check with each compound statement inside that statement
      for comp in list(self.statement_keys)[-1].compound_stmt:

        # If cursor is inside the compound statement, return false
        if (cursor.extent.start.line > comp.extent.start.line) or \
          (cursor.extent.start.column > comp.extent.start.column and cursor.extent.start.line == comp.extent.start.line):

            if (cursor.extent.end.line < comp.extent.end.line) or  \
              (cursor.extent.end.column < comp.extent.end.column and cursor.extent.end.line == comp.extent.end.line):
                
              return False

      # Else if the cursor is inside none of the compound statements, it must be in the condition, so return true 
      return True

    # If cursor isn't within most recent statement, return False
    return False
  
  def checkConditions(self, cursorToCheck):
    # For every statement in our dictionary
    for statement in list(self.statement_dict):
      # If the statement's body isn't empty
      if (statement.compound_stmt):
        # And the cursor is inside of the statement
        if cursorToCheck.extent.start.line >= statement.cursor.extent.start.line and cursorToCheck.extent.end.line <= statement.cursor.extent.end.line:
          
          # For each compound statement in the cursor
          for compound_stmt in statement.compound_stmt:
            # Check if the cursor is inside the compound statement (and thus in the body)
            if (compound_stmt.extent.end.line >= cursorToCheck.extent.end.line):
              
              # For each atomic condition in the statement
              for atomic_condition in self.statement_dict[statement]:
                  # Check if the cursor references the same cursor as the atomic condition
                  if atomic_condition.referenced.get_usr() == cursorToCheck.referenced.get_usr() and (atomic_condition != cursorToCheck):
                    # Set to check for a possible atomic write on the subsequent cursors
                    self.possibleAtomicWrite = (statement, cursorToCheck)
        # If the cursor is past the statement, remove the statement from the dictionary
        else:
          del self.statement_dict[statement]