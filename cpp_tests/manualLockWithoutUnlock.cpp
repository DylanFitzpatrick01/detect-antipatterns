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

std::string getState()
{
    std::lock_guard<std::mutex> lock(mDataAccess);          // Correctly locking for a read

    return mState;
}

void updateState(const std::string& input)
{
    mDataAccess.lock();                                     // Manually calling lock but never unlock the mutex!

    mState = input;
}

private:
    std::string mState;
    std::mutex mDataAccess;
};