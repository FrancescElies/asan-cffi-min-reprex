

typedef int int32_t;
typedef unsigned int uint32_t;

#define DllExport   __declspec( dllexport )

DllExport int32_t multiply(int32_t x, int32_t y);

typedef struct {
  uint32_t mock;
  uint32_t mock2;
} mystruct_depth2;

typedef struct {
  mystruct_depth2 boom[2];   // comment this line and test.py will not make asan explode ¯\_(ツ)_/¯
  /* mystruct_depth2 boom;   // This is OK. Uncomment this line and comment the previous one and see. */
} mystruct_depth1;

typedef struct {
  mystruct_depth1 mock;
} mystruct;
