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
    std::lock_guard<std::mutex> lock(mDataAccess);         // Correctly locking for a read
    return mState;
}

void updateState(const std::string& input)
{
    mDataAccess.lock();         // Correctly locking for a write

    mState = input;

    mDataAccess.unlock();
}

void logState()
{
    mDataAccess.lock();

    std::cout << "Current state: " << mState << "\n";

    mDataAccess.unlock();

    mDataAccess.lock();
    mDataAccess.unlock();

    mDataAccess.lock();
    mDataAccess.unlock();
}

private:
    std::string mState;
    std::mutex mDataAccess;
};