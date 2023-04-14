#include <atomic>
#include <chrono>
#include <iostream>
#include <thread>


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
        mThread = std::make_unique<std::thread>([this]() {

            while (!mStopping)
            {
                std::cout << "Doing some work, on thread " << std::this_thread::get_id() << "\n";
                std::this_thread::sleep_for(std::chrono::seconds(1));
            }

            });
    }

    void stop()
    {
        if (mThread)
        {
            mStopping = true;
            std::cout << "Stopping worker thread, on thread " << std::this_thread::get_id() << "\n";

            mThread->join();                            // https://en.cppreference.com/w/cpp/thread/thread/join
        }
    }

    ~MyClass()
    {
        std::cout << "MyClass desctructor, on thread " << std::this_thread::get_id() << "\n";

        stop();
    }

private:
    std::unique_ptr<std::thread> mThread;
    std::atomic<bool> mStopping;                    // This shared state is atomic, so it's safe to access on multiple threads.
};


int main()
{
    {
        auto instance = MyClass();

        instance.start();

        std::this_thread::sleep_for(std::chrono::seconds(5));

        instance.stop();                            // `stop()` calls `mThread->join()` so the internal thread joins at this point.
    }                                               // Now the destructor calls `mThread->join()` again, throw an exception.
                                                    // We need to check `mThread->joinable()` before calling `mThread->join()`


    std::cout << "Exiting program, on thread " << std::this_thread::get_id() << "\n";
}
