#include <iostream>
#include <string>
#include <mutex>

class MyClass
{
public:

MyClass(const std::string& input)
    : mState(input)
{
    
}

std::string& getState()                                      // Notice that the return type here is "string reference" rather than "string value"
{
    std::lock_guard<std::mutex> lock(mDataAccess);           // We are now locking a scope to provide synchonrisation for the data member
                                                            
    return mState;                                           // However, we then return a reference to the data member to the caller.
}

std::string* getStateP()                                     // Notice that the return type here is "string pointer" rather than "string value"
{
    std::lock_guard<std::mutex> lock(mDataAccess);           // We are now locking a scope to provide synchonrisation for the data member
                                                            
    return &mState;                                          // However, we then return a pointer to the data member to the caller.
}

void updateState(const std::string& input)
{
    std::lock_guard<std::mutex> lock(mDataAccess);

    mState = input;
}

private:
    std::string mState;
    std::mutex mDataAccess;
};

int main()
{
    MyClass instance("test123");

    std::string& referenceToInternalDataMember = instance.getState();

    std::string* pointerToInternalDataMember = instance.getStateP();

    // In both of these cases we now have access to something that we can read/write without the protection of the lock.

}