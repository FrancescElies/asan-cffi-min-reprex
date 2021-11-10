# 1 "c_src/example.h"
# 1 "<built-in>" 1
# 1 "<built-in>" 3
# 326 "<built-in>" 3
# 1 "<command line>" 1
# 1 "<built-in>" 2
# 1 "c_src/example.h" 2


typedef int int32_t;
typedef unsigned int uint32_t;



 int32_t multiply(int32_t x, int32_t y);

typedef struct {
  uint32_t mock;
  uint32_t mock2;
} mystruct_depth2;

typedef struct {
  mystruct_depth2 boom[2];

} mystruct_depth1;

typedef struct {
  mystruct_depth1 mock;
} mystruct;
