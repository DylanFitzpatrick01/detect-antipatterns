import abc
import clang.cindex
from typing import List
from .alerts import Alert

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
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        raise NotImplementedError