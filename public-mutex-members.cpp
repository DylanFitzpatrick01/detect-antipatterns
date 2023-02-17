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


    std::mutex mDataAccess1;  //public

    std::string getState()
    {
        std::mutex mDataAccess2; //private
        std::lock_guard<std::mutex> lock(mDataAccess2);          // Correctly locking for a read

        return mState;
    }
//
//    void updateState(const std::string& input)
//    {
//        std::mutex mDataAccess;                                     // Notice that the mutex is public!
//        std::lock_guard<std::mutex> lock(mDataAccess);          // Correctly locking for a write
//
//        mState = input;
//    }

    {
        {
        // do something
        }
        std::mutex mDataAccess3; //private
        void updateState(const std::string& input)
        {
            std::lock_guard<std::mutex> lock(mDataAccess1);

            mState = input;
        }
    }

     std::mutex mDataAccess4; //public

private:
    std::string mState;
};


int main()
{
    auto instance = MyClass("test123");

    std::cout << instance.getState() << "\n";                  // Good!

    instance.mDataAccess.lock();                               // Oh no!

}