from formalCheckInterface import FormalCheckInterface
import clang.cindex

class Check(FormalCheckInterface):
  def __init__(self):
    self.affected = dict()      # Dict of atomics and lists of affected vars
    self.investagating = list() # Stack of cursors

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

    elif cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR or cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
      if "std::atomic" in cursor.referenced.type.spelling:
        self.affected[cursor.referenced.get_usr()].append(self.investagating[-1].referenced)
      else:
        for key in self.affected:
          for var in self.affected[key]:
            if cursor.referenced.get_usr() == var.get_usr():
              self.affected[key].append(self.investagating[-1].referenced)

    for key in self.affected:
      print(key)
      for var in self.affected[key]:
        print("  ", var.get_usr())

    print()


    # if "std::atomic" in cursor.type.spelling:
    #   if cursor.kind == clang.cindex.CursorKind.VAR_DECL or cursor.kind == clang.cindex.CursorKind.FIELD_DECL:
    #     print("oh", cursor.spelling)
    #     print("atom:", cursor.referenced.get_usr())
    #     self.affected[cursor.referenced.get_usr()] = list()
    #     self.affected[cursor.referenced.get_usr()].append(cursor.referenced.get_usr())
    #   elif cursor.kind == clang.cindex.CursorKind.DECL_REF_EXPR or cursor.kind == clang.cindex.CursorKind.MEMBER_REF_EXPR:
    #     ref = cursor
    #     while ref.kind not in [clang.cindex.CursorKind.VAR_DECL,
    #                            clang.cindex.CursorKind.FIELD_DECL,
    #                            clang.cindex.CursorKind.PARM_DECL]:
    #       if ref.semantic_parent is None:
    #         print(ref.kind)
    #       ref = ref.semantic_parent
          
    
    
    # elif cursor.kind == clang.cindex.CursorKind.VAR_DECL:
    #   ref = cursor
    #   while ref.kind != clang.cindex.CursorKind.DECL_REF_EXPR:
    #     ref = list(ref.get_children())[0]
      
    #   # print(cursor.get_usr(), " = ", ref.referenced.get_usr())

    #   # If ref is in an affected list, cursor is now affected
    #   # TODO detect false postives, if affected is overwritten, remove it from
    #   #      list
    #   for key in self.affected:
    #     for usr in self.affected[key]:
    #       if usr == ref.referenced.get_usr():
    #         self.affected[key].append(cursor.get_usr())

  # If a cursor will be affected, add it
  def get_affected(cursor: clang.cindex.Cursor):
    # Handle: =, +, *, /, %, >>, <<        BinaryOperator
    #         +=, -=, *=, /=, %=, >>=, <<= CompoundAssignOperator
    #

    pass

  # appends all possible effects to the atomics list.
  def atomic_effect(cursor: clang.cindex.Cursor, atomics: list):
    pass