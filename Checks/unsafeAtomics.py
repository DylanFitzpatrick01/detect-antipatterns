from formalCheckInterface import FormalCheckInterface
from alerts import Alert
import clang.cindex
from Util import ConditionBodyStatement


class Check(FormalCheckInterface):
  statement_kinds = [clang.cindex.CursorKind.IF_STMT, clang.cindex.CursorKind.WHILE_STMT, clang.cindex.CursorKind.DO_STMT, clang.cindex.CursorKind.FOR_STMT]
  statement_dict = dict()        # Key - If statement cursor, Value - List of cursors in the if condition
  statement_keys = statement_dict.keys()  # The keys of statement_dict, so we can get the most recent if statement using [-1] indexing
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
    # If we found a statement, add it to the list
    if cursor.kind in self.statement_kinds:
      self.statement_dict[ConditionBodyStatement(cursor)] = list()
      list(self.statement_keys)[-1].compound_stmt = [child for child in list(cursor.get_children()) if child.kind == clang.cindex.CursorKind.COMPOUND_STMT]

    # Else if self.statement_dict is not empty     (since self.statement_keys = self.statement_dict.keys())
    elif (self.statement_keys):
      # Check if cursor is inside if statement
      if cursor.extent.start.line <= list(self.statement_keys)[-1].cursor.extent.end.line:
        # If the cursor belongs to a single check-then-set instruction
        if cursor.spelling == "compare_exchange_strong":
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
              if newAlert not in alerts:
                alerts.append(newAlert)

            elif cursor.type.spelling in self.possibleAtomicWrite[1].type.spelling and (cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR or cursor.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR):
              if newAlert not in alerts:
                alerts.append(newAlert)
            # TODO: Check if operator is always before the values written with?
            if not "operator" in cursor.displayname:
              self.possibleAtomicWrite = None

          if "std::atomic" in cursor.type.spelling and cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
            if (not self.nextAtomicIsCorrect):
              for statement in list(self.statement_dict):
                if (statement.compound_stmt):
                  if cursor.extent.start.line >= statement.cursor.extent.start.line and cursor.extent.end.line <= statement.cursor.extent.end.line:
                    for compound_stmt in statement.compound_stmt:
                      if (compound_stmt.extent.end.line >= cursor.extent.end.line):
                        for atomic_condition in self.statement_dict[statement]:
                            if atomic_condition.referenced.get_usr() == cursor.referenced.get_usr():
                              self.possibleAtomicWrite = (statement, cursor)
                  else:
                    del self.statement_dict[statement]
            else:
              self.nextAtomicIsCorrect = False
          
      
      else:
        del self.statement_dict[list(self.statement_keys)[-1]]
      

  def scope_increased(self, alerts):
    self.branchLevel += 1

  def scope_decreased(self, alerts):
    self.branchLevel -= 1

  def isInCondition(self, cursor, alerts):
    
    if (cursor.extent.start.line >= list(self.statement_keys)[-1].cursor.extent.start.line and \
          cursor.extent.end.line <= list(self.statement_keys)[-1].cursor.extent.end.line):
      for comp in list(self.statement_keys)[-1].compound_stmt:
        if (cursor.extent.start.line > comp.extent.start.line) or \
          (cursor.extent.start.column > comp.extent.start.column and cursor.extent.start.line == comp.extent.start.line):
            if (cursor.extent.end.line < comp.extent.end.line) or  \
              (cursor.extent.end.column < comp.extent.end.column and cursor.extent.end.line == comp.extent.end.line):
              return False
      return True
    return False