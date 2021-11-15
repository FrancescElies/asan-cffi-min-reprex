import cffi


ffi = cffi.FFI()
asanrt = ffi.dlopen(r"c:\s\eklang\DevOps\clang\bin\LLVM-13.0.0-win64\lib\clang\13.0.0\lib\windows\clang_rt.asan_dynamic-x86_64.dll")

import pdb  # comment this line and asan will not complain
