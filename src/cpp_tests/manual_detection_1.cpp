#include <mutex>

std::mutex a;
std::mutex b;
std::mutex c;

void test()
{
  a.lock();
  b.lock();

  if(true)
  {
    a.unlock();
  } else
  {
    b.unlock();
  }
}

int main()
{
  if(true)
  {
    test();
  } else
  {
    c.lock();
  }

  return 0;
}