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
    
    # A check should return true if the states of self and other are the same
    @abc.abstractmethod
    def equal_state(self, other) -> bool:
        raise NotImplementedError
    
    # All checks must be able to be duplicated
    @abc.abstractmethod
    def copy(self):
        raise NotImplementedError
    
    #Checks may not implement this unless they need to
    def scope_increased(self):
        pass

    # Check may not implement this unless they need to
    def scope_decreased(self):
        pass