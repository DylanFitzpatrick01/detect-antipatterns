#include <iostream>
#include <string>
#include <mutex>

class MyClass
{
public:

    MyClass(const std::string& input)
<<<<<<< HEAD
        : mState(input)                                         // No need to lock in a constructor. By definition, only the thread that creates the object has access to the object
=======
        : mState(input)                                          // No need to lock in a constructor. By definition, only the thread that creates the object has access to the object
>>>>>>> c8a675bf0958c7f26d5f7c2a9617242496900539
    {

    }

<<<<<<< HEAD
    //std::mutex mDataAccess1;                                     // Notice that the mutex is public!
    std::string getState()
    {
=======
    //std::mutex mDataAccess1;                                   // Notice that the mutex is public!
    std::string getState()
    {
        std::mutex mDataAccess2;                                 // mutex in scope so not public
>>>>>>> c8a675bf0958c7f26d5f7c2a9617242496900539
        std::lock_guard<std::mutex> lock(mDataAccess2);          // Correctly locking for a read

        return mState;
    }

    void updateState(const std::string& input)
    {
<<<<<<< HEAD
=======
        std::mutex mDataAccess2;                                 // mutex in scope so not public
>>>>>>> c8a675bf0958c7f26d5f7c2a9617242496900539
        std::lock_guard<std::mutex> lock(mDataAccess2);          // Correctly locking for a write
        mState = input;
        if(true){
            std::mutex mDataAccess3;
        }
        std::mutex mDataAccess4;
    }

<<<<<<< HEAD
    //std::mutex mDataAccess2;                                     // Notice that the mutex is public!
=======

>>>>>>> c8a675bf0958c7f26d5f7c2a9617242496900539

protected:
    std::mutex mDataAccess5;                                     // protected

private:
<<<<<<< HEAD
    std::string mState;                                     // private, not a mutex
=======
    std::string mState;                                          // private, not a mutex
>>>>>>> c8a675bf0958c7f26d5f7c2a9617242496900539
    std::mutex mDataAccess6;                                     // private
};


int main()
{
    auto instance = MyClass("test123");

<<<<<<< HEAD
    std::cout << instance.getState() << "\n";                  // Good!

    instance.mDataAccess2.lock();                               // Oh no!
=======
    std::cout << instance.getState() << "\n";                    // Good!

    //instance.mDataAccess2.lock();                              // Oh no!
>>>>>>> c8a675bf0958c7f26d5f7c2a9617242496900539

}