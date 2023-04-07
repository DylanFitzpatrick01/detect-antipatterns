#include <atomic>
#include <iostream>

// ANTIPATTERN: Detect issues with using atomics in ways that aren't actually thread safe 
// (Checking and then setting, rather than using a test and set instruction.)
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
    bool expected { false };
    for(int i = 0; mIsSet; i++) {
        if (i == 5) {
            mIsSet = false;
        }
    }
    while (mIsSet2)
    {
        mIsSet2 = false;
    }
    return -1;
}


void passFunction(int state)                                // CORRECT TEST-AND-SET OF ATOMIC
{
    bool expected { false };                                // This is the correct way to "read and write" an atomic in a single instruction (https://en.cppreference.com/w/cpp/atomic/atomic/compare_exchange)
    if (mIsSet.compare_exchange_strong(expected, true))     // We are saying "check if the value was false, and if it was then set it to true"
    {
        mState = state;
    }
    if (mIsSet.compare_exchange_strong(expected, true))
    {
        mIsSet = mIsSet2;                                    // Atomic to atomic writes are ok
    }                                     
}


void errorFunction(int state)
{
    bool expected { false };
    if(mIsSet.compare_exchange_strong(expected, true) && test)                 // The mistake is here, we first do a read and on the next line a write. This creates a chance that another thread
    {                           // can call the same method, at the same time and also end up updating the state.
        mIsSet = true;
        mState = state;
    }
}

void errorFunctionBool(bool cond)
{
    bool expected { false };
    if (mIsSet2)
    {
        if (test == false && mState == 10)
        {
            mIsSet2 = cond;
        }
    }
}
void ifElsePass(int state1, int state2)
{
    bool expected { false };
    if (mIsSet.compare_exchange_strong(expected, true))
    {
        mState = state1;
        if(mIsSet2.compare_exchange_strong(expected, true)) {
            mIsSet2 = false;
        }
    }
    else if (mState = 10)
    {
        mState = state2;
    }
    else
    {
        mState = state1;
        while(mIsSet2)
        {
            if (mIsSet)
            {
                mIsSet2 = true;
            }
        }
    }
}

void ifElseNestedError(int state1, int state2)
{
    bool expected { false };
    do {
        mIsSet = test;
    } while(!mIsSet);
    
}

private:
    bool test;
    std::atomic<bool> mIsSet;
    std::atomic<bool> mIsSet2;
    std::atomic<int> mInt;
    int mState;
};