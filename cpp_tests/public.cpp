#include <iostream>
#include <string>
#include <mutex>

class MyClass
{
public:

    MyClass(const std::string& input)
        : mState(input)   // No need to lock in a constructor. By definition, only the thread that creates the object has access to the object
    {

    }

    std::mutex mDataAccess1;  //public
    std::string mDataAccess2; //not a mutex

    std::string getState()
    {
        std::mutex mDataAccess3; //private
        std::lock_guard<std::mutex> lock(mDataAccess3);          // Correctly locking for a read

        return mState;
    }

    void updateState(const std::string& input)
    {
         {
        // do something
        }
        std::mutex mDataAccess4; //private
        std::string str; //not a mutex
        std::lock_guard<std::mutex> lock(mDataAccess4);
        mState = input;
    }

     std::mutex mDataAccess5; //public

protected:
    std::mutex mDataAccess6; //protected

private:
    std::string mState; //not a mutex
    std::mutex mDataAccess8;  //private

    std::string mState;
};

int main()
{
    //auto instance = MyClass("test123");

    MyClass instance("test123");

    std::cout << instance.getState() << "\n";                  // Good!

    instance.mDataAccess1.lock();                               // Oh no!
}