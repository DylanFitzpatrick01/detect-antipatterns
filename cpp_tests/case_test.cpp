#include <mutex>

std::mutex a;
std::mutex b;
std::mutex c;
std::mutex d;

void test()
{

}

int main()
{
  int x = 6;

  switch(x)
  {
    case 0:
      std::lock_guard<std::mutex> lock(d);
  }

  test();   //Should be unlocked

  switch(x)
  {
    case 0:
      a.lock();
    case 1:
      b.lock();
      break;
    
    case 2:
      b.lock();
    case 3:
      c.lock();
      break;
    
    case 4:
      c.lock();
      break;

  }

  test();   //Should be locked

  return 0;
}