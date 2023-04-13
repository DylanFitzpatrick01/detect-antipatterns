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
  test(); //No error

  {
    std::lock_guard<std::mutex> lock(a);

    test(); //error
  }

  b.lock();
  b.unlock();

  test(); //no error

  if(true)
  {
    c.lock();
  }

  test();   //error
  c.unlock();

  d.lock();
  if(true)
  {
    d.unlock();
  }

  test();   //error


  return 0;
}