#include <mutex>

std::mutex a;
std::mutex b;
std::mutex c;


void test()
{
    a.lock();

    // while(true)
    // {
    //     b.lock();
    // }
}

int main()
{
    // while(true)
    // {
    //     test();
    // }
    return 0;
}