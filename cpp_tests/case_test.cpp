#include <mutex>

std::mutex a;
std::mutex b;
std::mutex c;

int main()
{
  int x = 6;

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

  return 0;
}