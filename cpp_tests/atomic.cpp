#include <atomic>

struct testStruct
{
  int x;
  double y;
  std::atomic_bool z;
};

std::atomic_int32_t i;
std::atomic_int32_t j;
std::atomic_int32_t k;


std::atomic_bool b;
std::atomic<testStruct> c;

int main()
{
  bool a = b;

  int l = i + j;
  int m;
  m = i + j;

  m++;
  m += 5;
  m >>= 5;

  return 0;
}