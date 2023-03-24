#include <atomic>

std::atomic_bool b;

int main()
{
  bool a = b;
  
  bool c;
  c = b;

  bool d = false;

  b = c;

  return 0;
}
