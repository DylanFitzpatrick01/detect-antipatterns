#include <mutex>

std::mutex a;
std::mutex b;
std::mutex c;
std::mutex d;
std::mutex e;
std::mutex f;

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

void test3()
{
  switch(9)
  {
    case 0:
    case 1:
      e.lock();
      f.lock();
    break;
    case 2:
    case 3:
      f.lock();
    default:
      e.lock();
    break;
  }
}

int main()
{
  std::lock_guard<std::mutex> lockA(a);
  std::lock_guard<std::mutex> lockB(b); //Wrong order

  return 0;
}
