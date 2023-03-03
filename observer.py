import clang.cindex
from typing import List
# Gráinne Ready

# Observer INTERFACE, declares update method to be used in implementations of Observer interface
class Observer():            
    # Remember that Observer class is an INTERFACE, so update() remains EMPTY here
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
            self.kindList.append(currentNode)
            if currentNode.kind == self.kindToDetect:
                self.output += f"Detected variable {currentNode.type.spelling}: '{currentNode.displayname}' at {currentNode.location}\n"
                #print(f"{currentNode.displayname} found at {currentNode.location}")
                self.kindList.append(currentNode)


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