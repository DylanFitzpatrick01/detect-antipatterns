#include <mutex>

void test();

class a
{
public:
  a()
  {}

  void do_something()
  {
    x.lock();
    do_something_else();    //Okay, it is in the same class
    x.unlock();
  }

  void do_something_else()
  {
    
  }

  void do_something_else_else()
  {
    std::lock_guard<std::mutex> lock(x);

    test();                 //Out of this class, not okay
  }
private:
  std::mutex x;
};

void test()
{

}

int main()
{
  a b;

  b.do_something();

  b.do_something_else_else();
  return 0;
}