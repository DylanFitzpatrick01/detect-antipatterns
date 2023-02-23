from typing import List
# Gráinne Ready

# Observer INTERFACE, declares update method to be used in implementations of Observer interface
class Observer():            
    # Remember that Observer class is an INTERFACE, so update() remains EMPTY here
    def update(self, event: str):
        pass

# Observer IMPLEMENTATION, has a dedicated tag that it will detect, once that tag has been detected, it will update by printing
# said tag along with the event message. update() is to be called by eventSource()
class concreteObserver(Observer):
    def __init__(self, tagToDetect:str):
        self.tagToDetect = tagToDetect
        self.tagList = list()
    
    def update(self, currentNode):
        if self.tagToDetect == currentNode.type.spelling and currentNode not in self.tagList:
            self.tagList.append(currentNode)
            print(f"Detected a '{self.tagToDetect}', Name: {currentNode.spelling} at {currentNode.location}")
            if currentNode.spelling == "lock_guard":
                print(f"    Mutex Name: {list(currentNode.get_children())[0].spelling}")
                
        
# Subject class, has a list of observers which it notifies about events/state changes
class EventSource():
    # Initialises a list of observers
    def __init__(self):
        self.observers: List[Observer] = []

    # Notifies all observers in list with event
    def notifyObservers(self, event: str):
        for observer in self.observers:
            #print(event)
            observer.update(event)
    
    # Adds observer to list
    def addObserver(self, observer: Observer):
        self.observers.append(observer)
        
    def removeObserver(self, observer: Observer):
        if isinstance(observer, self.observers):
            self.observers.remove(observer)
        

class ObserverTest():
    def main():
        eventSource = EventSource()
        mutex_observer = concreteObserver(tagToDetect="std::mutex")
        lock_guard_observer = concreteObserver(tagToDetect="std::lock_guard<std::mutex")
        eventSource.addObserver(mutex_observer)
        eventSource.addObserver(lock_guard_observer)

    
    
if __name__ == "__main__":
    ObserverTest.main()