#include <mutex>

std::mutex a;
std::mutex b;
std::mutex c;
std::mutex d;

void test()
{
  std::lock_guard<std::mutex> lockB(b);
  std::lock_guard<std::mutex> lockA(a);
}

void test2()
{
  if(true)
  {
    c.lock();
    d.lock();
  } else
  {
    d.lock();
    c.lock(); //wrong order
  }
}

int main()
{
  std::lock_guard<std::mutex> lockA(a);
  std::lock_guard<std::mutex> lockB(b); //Wrong order

  return 0;
}