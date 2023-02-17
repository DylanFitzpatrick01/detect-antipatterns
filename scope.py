#Leon Byrne
#These are class for use with my locks.py file
#Could remove some and add some type variable instead

class Scope:
  def __init__(self):
    self.data = []

  def add(self, statement):
    self.data.append(statement)


  def empty(self):
    for a in self.data:
      if type(a) == Scope:
        if not a.empty():
          return False
      else:
        return False
    return True

class Lock:
  def __init__(self, mutex, location):
    self.mutex = mutex
    self.location = location

class Unlock:
  def __init__(self, mutex, location):
    self.mutex = mutex
    self.location = location

class LockGuard:
  def __init__(self, mutex, location):
    self.mutex = mutex
    self.location = location

class Locked:
  def __init__(self):
    self.order = []

  def lock(self, statement):
    error = False
    for lock in self.order:
      if lock.mutex == statement.mutex:
        error = True
    self.order.append(statement)
    return error

  #If this return false an error might occur as we are unlocking something that
  #we don't own, which may cause concurroncy errors
  def unlock(self, statement):
    removed = False
    for lock in self.order:
      if lock.mutex == statement.mutex:
        self.order.remove(lock)
        removed = True
    return removed
  
  def get_order(self):
    list = []
    for m in self.order:
      list.append(m.mutex)

    return list
  
class LockOrder:
  def __init__(self):
    self.orders = []

  def add(self, order):
    if not order in self.orders and len(order) > 1:
      self.orders.append(order)
    