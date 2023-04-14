#include <iostream>
#include <string>
#include <mutex>

class MyClass
{
public:

    MyClass(const std::string& input)
        : mState(input)                                          // No need to lock in a constructor. By definition, only the thread that creates the object has access to the object
    {

    }

    //std::mutex mDataAccess1;                                   // Notice that the mutex is public!
    std::string getState()
    {
        std::mutex mDataAccess2;                                 // mutex in scope so not public
        std::lock_guard<std::mutex> lock(mDataAccess2);          // Correctly locking for a read

        return mState;
    }

    void updateState(const std::string& input)
    {
        std::mutex mDataAccess2;                                 // mutex in scope so not public
        std::lock_guard<std::mutex> lock(mDataAccess2);          // Correctly locking for a write
        mState = input;
        if(true){
            std::mutex mDataAccess3;
        }
        std::mutex mDataAccess4;
    }



protected:
    std::mutex mDataAccess5;                                     // protected

private:
    std::string mState;                                          // private, not a mutex
    std::mutex mDataAccess6;                                     // private
};


int main()
{
    //auto instance = MyClass("test123");
    MyClass instance("test123");

    std::cout << instance.getState() << "\n";                    // Good!

    //instance.mDataAccess2.lock();                              // Oh no!

}