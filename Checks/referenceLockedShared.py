import clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import FormalCheckInterface


"""
A Check for some antipattern. analyse_cursor() runs for EVERY cursor!
"""

class Check(FormalCheckInterface):
  def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
    if str(cursor.kind) == "CursorKind.CXX_METHOD":
      # We're inside a function
      #   - Examine if the scope is locked (is there a lock guard or manual unlock?)
      #   - Examine the return type (pointer or reference)
      #       
      #       - If we return a pointer/reference from within a locked scope, trigger a warning

      # type.spelling is the function signature in the format : std::string &(int, char)

      signature = cursor.type.spelling
      signature = signature.split(" ")

      # signature[0] : std::string, void etc (return type)
      # signature[1] : (int, char), *(int) etc (arguments + pointer/ref)
      if signature[1][0] != "&" and signature[1][0] != "*":
        #The return type isn't a reference
        return

      if signature[0] == "void":
        #We don't return anything, this isn't a method we're concerned about
        return
            
      returnLoc = None
      for tk in cursor.get_tokens():
        if tk.spelling == "return":
          returnLoc = tk.location

      # returnLoc has the location of the return
      if isScopeLocked(cursor, returnLoc):
        # We return from within a locked scope
        newAlert = Alert(cursor.translation_unit, returnLoc, "Warning: A reference to shared data from a locked scope"
                         + " is returned!", severity="warning")
        if newAlert not in alerts:
          alerts.append(newAlert)
                                                                   
    
# Is the scope within the extent of 'cursor' locked?
def isScopeLocked(cursor: clang.cindex.Cursor, loc: clang.cindex.SourceLocation) -> bool:
  # First figure out which line contains a lock
  lockPresent = False
  lockLine = None

  lockTypes = ["std::mutex", "mutex", "std::lock_guard<std::mutex>", "lock_guard<mutex>"]
  # RAII locks first:
  for c in cursor.walk_preorder():
    #print(str(c.location) + " " + str(c.type.spelling))
    if c.type.spelling in lockTypes:
            
      line = c.location.line
      if lockLine != None:
        lockLine = min(lockLine, line)
      else:
        lockLine = line
      if loc.line >= lockLine:
        lockPresent = True

    
  return lockPresent