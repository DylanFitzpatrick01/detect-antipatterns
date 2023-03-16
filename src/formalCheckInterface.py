import abc
import clang.cindex
from typing import List
from alerts import Alert

# An interface for all Checks, which should inherit this class.
class FormalCheckInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass) -> None:
        return (hasattr(subclass, 'analyse_cursor') and
                callable(subclass.analyse_cursor) or
                NotImplemented)

    def __init__(self) -> None:
        self.alerts: List(Alert) = list()

    # All Checks should implement the "analyse_cursor()" method.
    @abc.abstractmethod
    def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
        raise NotImplementedError

    def __eq__(self, __o: object) -> bool:
        return type(self) == type(__o)
    
    # All checks must be able to be duplicated
    def copy(self):
        return self
    
    #Checks may not implement this unless they need to
    def scope_increased(self, alerts):
        pass

    # Check may not implement this unless they need to
    def scope_decreased(self, alerts):
        pass

    def new_function(self, alerts):
        pass