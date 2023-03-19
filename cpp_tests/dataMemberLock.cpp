#include <iostream>
#include <string>
#include <mutex>

class MyClass
{
public:

    MyClass(const std::string& input)
        : mState(input)                                         // No need to lock in a constructor. By definition, only the thread that creates the object has access to the object
    {

    }

    std::string getState()
    {
        std::lock_guard<std::mutex> lock(mDataAccess);          // Correctly locking for a read

        return mState;
    }

    void updateState(const std::string& input)
    {
        std::lock_guard<std::mutex> lock(mDataAccess);          // Correctly locking for a write

        mState = input;
    }

    std::string mState;                                         // Notice that these members are public!
    std::mutex mDataAccess;
};


int main()
{
    auto instance = MyClass("test123");

    std::cout << instance.getState() << "\n";                  // Good! 

    std::cout << instance.mState << "\n";                      // Bad

}