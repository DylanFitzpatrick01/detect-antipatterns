#include <atomic>
#include <chrono>
#include <iostream>
#include <thread>
#include <memory>


class MyClass
{
public:

MyClass()
    : mStopping(false)
{
    std::cout << "Creating MyClass instance, on thread " << std::this_thread::get_id() << "\n";
}

void start()
{
    std::cout << "Starting worker thread, on thread " << std::this_thread::get_id() << "\n";
    mThread1 = std::make_unique<std::thread>([this](){

        while(!mStopping)
        {
            std::cout << "Doing some work, on thread " << std::this_thread::get_id() << "\n";
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

    });
}

void stop()
{
    if(mThread1)
    {
        mStopping = true;
        std::cout << "Stopping worker thread, on thread " << std::this_thread::get_id() << "\n";

        if(mThread1->joinable())
        {
            mThread1->join();
        }
    }
}

~MyClass()
{
    std::cout << "MyClass desctructor, on thread " << std::this_thread::get_id() << "\n";
    if(mThread1)
    {
        mStopping = true;
        std::cout << "Stopping worker thread, on thread " << std::this_thread::get_id() << "\n";
//        if(mThread1->joinable())
//        {
//            mThread1->join();
//        }
        if(mThread3->joinable())
        {
            mThread3->detach();
        }
    }
std::cout << "Creating MyClass instance, on thread " << std::this_thread::get_id() << "\n";
}


private:
    std::unique_ptr<std::thread> mThread1;
    std::unique_ptr<bool> mBool;
    std::thread mThread2;
    std::thread* mThread3;
    std::atomic<bool> mStopping;                    // This shared state is atomic, so it's safe to access on multiple threads.
};


int main()
{

    // Scenario 1, correct usage
    {
        auto instance = MyClass();

        instance.start();

        std::this_thread::sleep_for(std::chrono::seconds(5));

        instance.stop();
    }

    // Scenario 2, incorrect usage... forget to call `stop()` before destruction
    {
        auto instance = MyClass();

        instance.start();

        std::this_thread::sleep_for(std::chrono::seconds(5));

    }   // In this case we end up calling the std::thread destructor without calling `join()`
        // This is illegal and the program will exit, we wont get to the log line below.

    std::cout << "Exiting program, on thread " << std::this_thread::get_id() << "\n";
}

        // There's a design problem in `MyClass`. We are relying on the consumer to call `stop()`
        // before the object is destroyed.

        // It would be much better if we designed our class so the consumer doesnt need to remember
        // to do this.

        // The way to achieve this is to make sure  that the destructor itself handles the joining.
        // Then we dont even need a `stop()`.

        /** For example:

            ~MyClass()
            {
                std::cout << "MyClass desctructor, on thread " << std::this_thread::get_id() << "\n";

                if(mThread)
                {
                    mStopping = true;
                    std::cout << "Stopping worker thread, on thread " << std::this_thread::get_id() << "\n";

                    if(mThread->joinable())
                    {
                        mThread->join();
                    }

                }
            }
        **/