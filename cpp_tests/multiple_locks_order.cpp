#include <iostream>
#include <string>
#include <mutex>

class MyClass
{
public:

MyClass(const std::string& input)
    : mState(input)  
    , mOtherState(0)                                      
{

}

std::string calculateUpdatedState()
{
    std::lock_guard<std::mutex> lock(mMutex1);                  // In this function we lock in the order mMutex1 then mMutex2

    if(mOtherState > 0)
    {
        std::lock_guard<std::mutex> lock(mMutex2);

        mState = mState + mState;

        return mState;
    }

    return std::string();
}

void setState(const std::string& input)
{
    std::lock_guard<std::mutex> lock(mMutex2);                  // In this function we lock in the order mMutex2 then mMutex1

    if(!input.empty())
    {
        std::lock_guard<std::mutex> lock(mMutex1);

        mOtherState = input.size();
    }

    mState = input;
}

private:
    std::string mState;
    int mOtherState;
    std::mutex mMutex1;
    std::mutex mMutex2;                                         // In general, it's best to avoid multiple locks unless we really need them.
                                                                // And if we do really need them we need to ensure that the order of locking is the same
};