#include <mutex>

std::mutex a;

void test()
{
    while(true)
    {
        a.lock();
    }
}

int main()
{
    test();
    return 0;
}