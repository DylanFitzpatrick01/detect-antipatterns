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
        """Initialiser
        Initialises three members,
            self.tagToDetect(str)
            self.tagList(list)
            self.output(str)

        Args:
            tagToDetect (str): The Cursor.type.spelling to detect
        """
        self.tagToDetect = tagToDetect
        self.tagList = []
        self.output = ""


    def update(self, currentNode):
        """Updates the observer with the currentNode

        Args:
            currentNode (clang.cindex.Cursor): The node to update with
        """
        if currentNode not in self.tagList:
            if self.tagToDetect == currentNode.type.spelling:
                self.tagList.append(currentNode)

                if self.tagToDetect == "std::mutex" and currentNode.displayname != 'class std::mutex' and currentNode.type.spelling == self.tagToDetect:
                        self.output += f"Detected a '{self.tagToDetect}', Name: '{currentNode.spelling}' at {currentNode.location}\n"
                        #print(f"Detected a '{self.tagToDetect}', Name: '{currentNode.spelling}' at {currentNode.location}")

                elif self.tagToDetect == "std::lock_guard<std::mutex>" and currentNode.spelling == "lock_guard":
                        self.output += f"Detected a '{self.tagToDetect}' Lockguard's Name: '{currentNode.spelling}' at {currentNode.location}\n"
                        #print(f"Detected a '{self.tagToDetect}' Lockguard's Name: '{currentNode.spelling}' at {currentNode.location}")
                

class cursorKindObserver(Observer):
    def __init__(self, kindToDetect: clang.cindex.CursorKind):
        """Initialiser
        Initialises three members,
            self.kindToDetect(clang.cindex.CursorKind)
            self.kindList(list)
            self.output(str)

        Args:
            kindToDetect (str): The clang.cindex.CursorKind to detect
        """
        self.kindToDetect = kindToDetect
        self.kindList = []
        self.output = ""


    def update(self, currentNode):
        """Updates the observer with the currentNode

        Args:
            currentNode (clang.cindex.Cursor): The node to update with
        """
        if currentNode not in self.kindList:
            if currentNode.kind == self.kindToDetect:
                self.output += f"Detected {currentNode.type.spelling}: '{currentNode.displayname}' at {currentNode.location}\n"
                self.kindList.append(currentNode)


class cursorTypeKindObserver(Observer):
    def __init__(self, typeKindToDetect: clang.cindex.TypeKind):
        """Initialiser
        Initialises three members,
            self.typeKindToDetect(clang.cindex.TypeKind)
            self.typeKindList(list)
            self.output(str)

        Args:
            typeKindToDetect (str): The clang.cindex.TypeKind
        """
        self.typeKindToDetect = typeKindToDetect
        self.typeKindList = []
        self.output = ""


    def update(self, currentNode):
        """Updates the observer with the currentNode

        Args:
            currentNode (clang.cindex.Cursor): The node to update with
        """
        self.typeKindList.append(currentNode)
        if currentNode.type.kind == self.typeKindToDetect:
            self.output += f"Detected {currentNode.type.spelling}: '{currentNode.displayname}' at {currentNode.location}\n"
            self.typeKindList.append(currentNode)


# Gráinne Ready
# Subject class, has a list of observers which it notifies about events/state changes
class EventSource():
    # Initialises a list of observers
    def __init__(self):
        """Initialiser
        Initialises with one data member, an empty list for Observers
        """
        self.observers = []


    # Notifies all observers in list with event
    def notifyObservers(self, event: clang.cindex.Cursor):
        """Updates all observers in the EventSource list with an event

        Args:
            event (clang.cindex.Cursor): The cursor to update observers with
        """
        for observer in self.observers:
            observer.update(event)


    # Adds observer to list
    def addObserver(self, observer: Observer):
        """Adds an observer to the EventSource list

        Args:
            observer (Observer): The observer to add to the EventSource list
        """
        self.observers.append(observer)


    def addMultipleObservers(self, observers: List[Observer]):
        """Adds observers from a list into the EventSource list

        Args:
            observers (List[Observer]): A list of Observers to add to the EventSource
        """
        self.observers.extend(observers)


    def removeObserver(self, observer: Observer):
        """Removes an Observer from the EventSource list, if it is an element of it.

        Args:
            observer (Observer): The observer to remove
        """
        if observer in self.observers:
            self.observers.remove(observer)


    def removeMultipleObservers(self, observers: List[Observer]):
        """Removes multiple observers from the EventSource list, checking if each is an element
        of the list before it attempts to remove it

        Args:
            observers (List[Observer]): The list of observers to remove from the EventSource list
        """
        for observer in observers:
            if observer in self.observers:
                self.observers.remove(observer)
                
def searchNodes(file_path : str, eventSrc: EventSource):
    """
    Searches through every node in a c++ file (AST) and notifies Observers in the EventSource about it
    
    Args:
        file_path (str): The path of the c++ file to check for the antipattern
        eventSrc (EventSource): The EventSource object to notify observer with
    
    Returns:
        None
    """
    index = clang.cindex.Index.create()
    tu = index.parse(file_path)
    for cursor in tu.cursor.walk_preorder():
        # This if statement makes sure only nodes that are inside the file itself are fed into the Observers
        if(str(cursor.translation_unit.spelling) == str(cursor.location.file)):
            eventSrc.notifyObservers(cursor)