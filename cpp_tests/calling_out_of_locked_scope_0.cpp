#include <mutex>

std::mutex a;
std::mutex b;
std::mutex c;

void test1()
{

}

void test2()
{
  std::lock_guard<std::mutex> lock(c);

  test1();    //c is locked within this scope
}

int main()
{
  if(true)
  {
    a.lock();
  } else
  {
    a.unlock();
  }

  test1();    //Possible that a will be locked above
  a.unlock();

  {
    std::lock_guard<std::mutex> lock(b);

    test1();  //b is locked in this scope
  }

  test1();    //None are locked right now

  test2();    //None are locked right now

  return 0;
}