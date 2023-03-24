#include <atomic>

std::atomic_bool b;

int main()
{
  bool a = b;     //Not atomic series of operations.
  bool c;         //
  c = b;          //
  bool d = false; //
  b = c;          //Error, b may have been changed since read above.

  b = d;          //No error, d is independant of b.

  return 0;
}
