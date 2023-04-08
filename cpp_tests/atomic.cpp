#include <atomic>
#include <stdio.h>

std::atomic_int x;
std::atomic_int y;
std::atomic_int z;

int main()
{
  // non atomic series of operations applied to atomic
  // section equivalent to x += 5, (x = x + 10) * 5
  int a = x.fetch_add(5);     //
  a += 10;                    //
  int b = a * 5;              //
  x = b;                      // error, x may have changed since loaded

  // Non atomic series of operations, not applied to atomic
  // section equivalent to c = (c & y) | 10
  int c;                      //
  c = c & y;                  //
  c |= 10;                    //

  // atomic operation applied to atomic
  // section equivalent to y = 5
  c = 5;
  printf("y is %d\n", (int) y); // test algorithm, may screw up test if no measures taken
  y = c;                        // no error, y does not depend on previous state

  // non atomic series of operations applied to atomic
  // section equivalent to z = z
  int d = z;
  d = z.exchange(d);            // error, z may have changed since loaded


  return 0;
}
