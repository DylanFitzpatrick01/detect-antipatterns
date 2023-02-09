#include <iostream>
#include <memory>
#include <mutex>

class IMyCallback                              						// Callback interface
{
public:
   virtual ~IMyCallback() = 0;

   virtual void onSomethingHappend(int value) = 0;
   virtual void onErrorHappend() = 0;
};

class MyClass                                                       // Class that needs to be made threadsafe.
{
public:
    MyClass(std::shared_ptr<IMyCallback> callback)
        :  mCallback(callback)
    {}

    void doSomething()
    {
        {
            std::lock_guard<std::mutex> lock(mDataMutex);           // CriticalSection starts

            calculate();

            mCallback->onSomethingHappend(mInternalState);          // Uh oh! We're calling outside of a locked scope
        }                                                           // CriticalSection ends
    }

    int readState()
    {
        std::lock_guard<std::mutex> lock(mDataMutex);               // Accessing the same lock as in `doSomething()`

        return mInternalState;
    }

private:

    void calculate()
    {
        mInternalState = mInternalState + 1;                        // Modifying some internal state that needs to be synchronised.
    }

   std::shared_ptr<IMyCallback> mCallback;
   std::mutex mDataMutex;
   int mInternalState = 0;
};


class ReEntrantCallbackImpl : public IMyCallback                     // Implementation of callback interface 
{
public:
    ReEntrantCallbackImpl()
    {
    }

    void init(std::shared_ptr<MyClass> myClass)
    {
        mMyClass = myClass;
    }

    void onSomethingHappend(int value) override
    {
        std::cout << "Current value is: " << mMyClass->readState(); // Calling `mMyClass->readState()` will access the lock. 
    }

    void onErrorHappend() override
    {

    }
 private:
  std::shared_ptr<MyClass> mMyClass;
};

int main()
{
    auto callback = std::make_shared<ReEntrantCallbackImpl>();

    auto myClass = std::make_shared<MyClass>(callback);
    callback->init(myClass);

    myClass->doSomething();                                         // Deadlock or crash
}