#include <mutex>

class MyClass
{
public:
  MyClass()
  {

  }

  std::mutex a;
};

std::mutex a;
std::mutex b;
std::mutex c;
std::mutex d;

int main()
{
  MyClass myClass;

  {
    std::lock_guard<std::mutex> lock(a);
  }

  a.lock();           //No error

  if(true)
  {
    a.lock();         //error
  }

  myClass.a.lock();   //no error, my class's a is different

  while(true)
  {
    b.lock();         //error
  }

  do
  {
    c.lock();         //error
  } while(true);

  for(int i = 0; i < 10; i++)
  {
    d.lock();         //error
  }

  return 0;
}