import os

import cffi

clang_rt = os.environ["clang_rt_path"]
ffi = cffi.FFI()
asanrt = ffi.dlopen(clang_rt)

import pdb  # comment this line and asan will not complain
