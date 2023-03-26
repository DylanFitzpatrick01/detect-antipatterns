#include <atomic>
#include <iostream>

class MyClass
{
public:

MyClass()
    : mIsSet(false)
    , mState(0)
{

}


// Atomics are a special type of concurrency primitive, provided by the CPU architecture, which allow us to implement "lock free" algorithms

// The CPU guarantees that all reads and writes to the atomic are thread safe. As well as reads and writes, we also have a special "read and write in one" instruction.

// However, they can only be used in very particular ways, and they work very differently to locks/mutexes.

int getState()
{
    if(mIsSet)
    {
        return mState;
    }
    
    return -1;
}

void passFunction(int state)
{
    bool expected { false };                                // This is the correct way to "read and write" an atomic in a single instruction (https://en.cppreference.com/w/cpp/atomic/atomic/compare_exchange)
    if (mIsSet.compare_exchange_strong(expected, true))     // We are saying "check if the value was false, and if it was then set it to true"
    {                                                       // This all happens in one CPU instruction that cannot be interleaved, so this is thread safe
        mIsSet = false;
    }
}

void errorFunction1(int state)
{
    bool expected{ false };
    if (mIsSet.compare_exchange_strong(expected, true))     // PASS: Will perform read and write in single instruction
    {                                                       
        mIsSet = false;                                     // FAIL: This write isn't thread safe
    }
    else {
        mIsSet = true;                                      // FAIL: This write isn't thread safe
    }
}

void errorFunction2(int state)
{
    int expected = 10;
    if (mInt.compare_exchange_strong(expected, 16)) // PASS: Will perform read and write in single instruction
    {
        std::cout << "Value of mInt was 10 but is now 16" << std::endl;
        if (!mIsSet)                                                                    // FAIL: This read isn't thread safe
        {
            mInt = state;                                                               // FAIL: This write isn't thread safe
            std::cout << "Value of mInt was 16 but is now" << mInt << std::endl;        // FAIL: This read isn't thread-safe
        }
    }
    else
    {
        std::cout << "Value of mInt was not 10, so no changes were made";
    }
}


private:
    std::atomic<bool> mIsSet;
    std::atomic<int> mInt;
    int mState;
};