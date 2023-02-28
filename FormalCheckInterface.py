import abc
import clang.cindex

class FormalCheckInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'analyse_cursor') and
                callable(subclass.analyse_cursor) or
                NotImplemented)

    @abc.abstractmethod
    def analyse_cursor(cursor: clang.cindex.Cursor):
        raise NotImplementedError