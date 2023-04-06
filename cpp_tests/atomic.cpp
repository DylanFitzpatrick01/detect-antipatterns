#include <atomic>

std::atomic_bool b;
std::atomic_int x;
std::atomic_int y;

int main()
{
  // bool a = b;     //Not atomic series of operations.
  // bool c;         //
  // c = b;          //
  // b = c;          //Error, b may have been changed since read above.

  // bool d = false;
  // b = d;          //No error, d is independant of b.

  int z = x * y;  // 
  x = z;          // error 
  z = 5;          //
  x += z;         // no error


  return 0;
}
