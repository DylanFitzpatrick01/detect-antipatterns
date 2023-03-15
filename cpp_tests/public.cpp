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

    {
        {
        // do something
        }
        std::mutex mDataAccess4; //private
        void updateState(const std::string& input)
        {
            std::lock_guard<std::mutex> lock(mDataAccess4);

            mState = input;
        }
    }

     std::mutex mDataAccess5; //public

protected:
    std::mutex mDataAccess6; //private

private:
    std::string mDataAccess7; //not a mutex
    std::mutex mDataAccess8;  //private
};

int main()
{
    auto instance = MyClass("test123");

    std::cout << instance.getState() << "\n";                  // Good!

    instance.mDataAccess.lock();                               // Oh no!

}