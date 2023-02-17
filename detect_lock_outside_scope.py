from typing import List

AST_path = r"AST.txt"

# I'd assume it might make it easier if we took a note of what line number the locks/unlocks etc. are on?
class Observer():            
    # Remember that Observer class is an interface, so update() remains empty here
    def update(self, event: str):

    	pass

#TODO: Implement Observer properly, this class is just a simple implementation so that we can see it receives responses
#        update() function needs to be expanded on!
class updateObserver(Observer):
    def update(self, event:str):
        print(f"Received response: {event}")
        
        
class EventSource():
    def __init__(self):
        self.observers: List[Observer] = []

    def notifyObservers(self, event: str):
        for observer in self.observers:
            observer.update(event)
    
    def addObserver(self, observer: Observer):
        self.observers.append(observer)
    
    def readAST(self):
        # Assume we read through AST.txt here?
        with open(AST_path, "r") as lines:
            for line in lines:
                self.notifyObservers(line)

class ObserverDemo():
    def main():
        eventSource = EventSource()

        # Couldn't get the lambda/event to work properly in python so I tried this instead in the meantime and created updateObserver which does the print statements instead
        observer = updateObserver()
        eventSource.addObserver(observer)

        eventSource.readAST()
    
    
if __name__ == "__main__":
    ObserverDemo.main()