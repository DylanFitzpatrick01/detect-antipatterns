from formalCheckInterface import FormalCheckInterface
from alerts import Alert
import clang.cindex

class Check(FormalCheckInterface):
  def __init__(self):
    self.affected = dict()      # Dict of atomics and lists of affected vars
    self.investagating = list() # Stack of cursors
    self.skipNext = False

    self.atomicWrite = False

    self.branchLevel = 0        # The level of branches we're in. 0 is none, >1
                                # is a nested branch

  # When a var will be changed, add it to the stack. When moved on, remove it
  # If entered method tell it next return

  def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
    if cursor.kind == clang.cindex.CursorKind.VAR_DECL or cursor.kind == clang.cindex.CursorKind.FIELD_DECL:
      if "std::atomic" in cursor.type.spelling:
        self.affected[cursor.referenced.get_usr()] = list()
      else:
        if len(self.investagating) > 1:
          self.investagating.pop()
        self.investagating.append(cursor)
    elif cursor.kind == clang.cindex.CursorKind.CALL_EXPR and cursor.spelling == "operator=":
      if "std::atomic" in list(cursor.get_children())[0].type.spelling:
        self.atomicWrite = True
        if len(self.investagating) > 1:
          self.investagating.pop()
          self.investagating.append(list(cursor.get_children())[0])
          self.skipNext = True
    elif cursor.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
      self.atomicWrite = False
      if len(self.investagating) > 1:
        self.investagating.pop()
      self.investagating.append(list(cursor.get_children())[0])
      self.skipNext = True

    elif cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR or cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
      # Atomic to atomic writes arer okay, don't investigate
      if "std::atomic" in cursor.referenced.type.spelling and "std::atomic" not in self.investagating[-1].referenced.type.spelling:
        self.affected[cursor.referenced.get_usr()].append(self.investagating[-1].referenced)
      elif not self.skipNext:
        if self.atomicWrite:
          for key in self.affected:
            for var in self.affected[key]:
              if cursor.referenced.get_usr() == var.get_usr():
                newAlert = Alert(self.investagating[-1].translation_unit, self.investagating[-1].extent, 
                                 "This appears to be the end of a non-atomic series of operations.")
                if newAlert not in alerts:
                  alerts.append(newAlert)
                print("error")
        else:
          for key in self.affected:
            for var in self.affected[key]:
              if cursor.referenced.get_usr() == var.get_usr():
                self.affected[key].append(self.investagating[-1].referenced)
      elif self.skipNext:
        self.skipNext = False

    # for key in self.affected:
    #   print(key)
    #   for var in self.affected[key]:
    #     print("  ", var.get_usr())

  def enter_branch(self, alerts):
    self.branchLevel += 1
    # Might be useful for you to use 

  def exit_branch(self, alerts):
    self.branchLevel -= 1