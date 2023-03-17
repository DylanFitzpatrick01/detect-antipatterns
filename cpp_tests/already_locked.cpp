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

int main()
{
  MyClass myClass;

  {
    std::lock_guard<std::mutex> lock(a);
  }

  a.lock(); //No error

  if(true)
  {
    a.lock(); //error
  }

  myClass.a.lock();  //no error, my class a is different

  return 0;
}