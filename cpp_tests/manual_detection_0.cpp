#include <mutex>

std::mutex a;
std::mutex b;
std::mutex c;

int main()
{
  a.lock();

  if(true)
  {
    b.lock();
  } else if(true)
  {
    if(true)
    {
      a.unlock();
    } else
    {
      b.unlock();
    }
  } else
  {
    c.unlock();
  }

  return 0;
}