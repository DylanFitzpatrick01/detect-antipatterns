import clang.cindex
from typing import List
# Gráinne Ready

# Observer INTERFACE, declares update method to be used in implementations of Observer interface
class Observer():            
    def update(self, event: str):
        pass


# Observer IMPLEMENTATION, has a dedicated tag that it will detect, once that tag has been detected, it will update by printing
# said tag along with the event message. update() is to be called by eventSource()
class tagObserver(Observer):
    def __init__(self, tagToDetect:str):
        self.tagToDetect = tagToDetect
        self.tagList = list()
        self.output = ""


    def getList(self):
        return self.tagList


    def update(self, currentNode):
        if currentNode not in self.tagList:
            if self.tagToDetect == currentNode.type.spelling:
                self.tagList.append(currentNode)

                if self.tagToDetect == "std::mutex" and currentNode.displayname != 'class std::mutex':
                        self.output += f"Detected a '{self.tagToDetect}', Name: '{currentNode.spelling}' at {currentNode.location}\n"
                        #print(f"Detected a '{self.tagToDetect}', Name: '{currentNode.spelling}' at {currentNode.location}")

                elif self.tagToDetect == "std::lock_guard<std::mutex>" and currentNode.spelling == "lock_guard":
                    if currentNode.spelling == "lock_guard":
                        self.output += f"Detected a '{self.tagToDetect}' Lockguard's Name: '{currentNode.spelling}' at {currentNode.location}\n"
                        #print(f"Detected a '{self.tagToDetect}' Lockguard's Name: '{currentNode.spelling}' at {currentNode.location}")  


# Gráinne Ready
# An Observer which looks for a specific clang.cindex.CursorKind
# @Param kindToDetect:  The clang.cindex.cursorKind to find
class cursorKindObserver(Observer):
    def __init__(self, kindToDetect:str):
        self.kindToDetect = kindToDetect
        self.kindList = list()
        self.output = ""


    def update(self, currentNode):
        if currentNode not in self.kindList:
            if currentNode.kind == self.kindToDetect:
                self.output += f"Detected {currentNode.type.spelling}: '{currentNode.displayname}' at {currentNode.location}\n"
                print(f"Detected {currentNode.type.spelling}: '{currentNode.displayname}' at {currentNode.location}\n")
                self.kindList.append(currentNode)


class CompoundStatementObserver(Observer):
    def __init__(self):
        self.unnamed_lock_guards = []
        self.lock_guards_missing_mutex = []
        self.complete_lock_guards = []
        self.output = ""


    def update(self, currentNode):
        if currentNode.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            for token in currentNode.get_tokens():
                if (token.kind == clang.cindex.TokenKind.IDENTIFIER):
                    if (token.spelling == "lock_guard"):
                        self.unnamed_lock_guards.append(lock_guard(token, None, None))
                    else:
                        self.checkIfPartOfLockGuards(token)


    def checkIfPartOfLockGuards(self, token : clang.cindex.Token):

        if len(self.unnamed_lock_guards) > 0:
            found_lock_name = False
            while (not found_lock_name):
                for lock_grd in self.unnamed_lock_guards:
                    if (token.location.column - 23 == lock_grd.lock_token.location.column and token.location.line == lock_grd.lock_token.location.line):
                        lock_grd.setLockName(token)
                        self.lock_guards_missing_mutex.append(lock_grd)
                        self.unnamed_lock_guards.remove(lock_grd)
                        found_lock_name = True
                break

        if len(self.lock_guards_missing_mutex) > 0:
            found_mutex_name = False
            while (not found_mutex_name):
                for lock_grd in self.lock_guards_missing_mutex:
                    if (token.location.column - 28 == lock_grd.lock_token.location.column and token.location.line == lock_grd.lock_token.location.line):
                        lock_grd.setMutexName(token)
                        self.complete_lock_guards.append(lock_grd)
                        self.output += f"Detected a lock_guard called '{lock_grd.lock_name.spelling}' guarding mutex called '{lock_grd.mutex_name.spelling}' at {lock_grd.lock_token.location}\n"
                        self.lock_guards_missing_mutex.remove(lock_grd)
                        found_mutex_name = True
                break


    def printLockGuards(self):
        for lock in self.complete_lock_guards:
            print(f"Detected a lock_guard called '{lock.lock_name.spelling}' guarding mutex called '{lock.mutex_name.spelling}' at {lock.lock_token.location}\n")
                        

                        
                    


# Gráinne Ready
# Subject class, has a list of observers which it notifies about events/state changes
class EventSource():
    # Initialises a list of observers
    def __init__(self):
        self.observers = []


    # Notifies all observers in list with event
    def notifyObservers(self, event: str):
        for observer in self.observers:
            observer.update(event)


    # Adds observer to list
    def addObserver(self, observer: Observer):
        self.observers.append(observer)


    def addMultipleObservers(self, observers: List[Observer]):
        for observer in observers:
            self.observers.append(observer)


    def removeObserver(self, observer: Observer):
        if observer in self.observers:
            self.observers.remove(observer)


    def removeMultipleObservers(self, observers: List[Observer]):
        for observer in observers:
            if observer in self.observers:
                self.observers.remove(observer)

class lock_guard():
    def __init__(self, lock_token : clang.cindex.Token, lock_name: clang.cindex.Token, mutex_name : clang.cindex.Token):
        self.lock_token = lock_token
        self.lock_name = lock_name
        self.mutex_name = mutex_name
    
    def setMutexName(self, name_token : clang.cindex.Token):
        self.mutex_name = name_token
    
    def setLockName(self, name_token : clang.cindex.Token):
        self.lock_name = name_token