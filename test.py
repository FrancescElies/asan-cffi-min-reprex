import re
import unittest
from pathlib import Path

import cffi

from build import build

file_path = Path(__file__).absolute()
file_directory = file_path.parent


def cleanCDEF(cdef: str):
  cdef = cdef.replace("__declspec( dllexport )", "")
  return cdef


def test_example(asan=False):
  ffiPath = file_directory / "c_src/ffi.i"
  ffi = cffi.FFI()
  clean_ffi = (file_directory / "c_src/clean_ffi.i")
  clean_ffi.write_text(cleanCDEF(ffiPath.read_text()))
  ffi.cdef(clean_ffi.read_text(), pack=8)
  if asan:
    dllPath = file_directory / "c_src/asanexample.dll"
  else:
    dllPath = file_directory / "c_src/example.dll"
  print(f"dlopen {dllPath}")
  C = ffi.dlopen(str(dllPath.absolute()))

  mystruct = ffi.new("mystruct *")
  print(f'OK test_example {asan=}')


class Mytest(unittest.TestCase):
  def dummy_test(self):
    ...


if __name__ == '__main__':
  build()

  # This seems ok, but not sure
  test_example()
  test_example(asan=True)

  # unittest explodes BOOM
  unittest.main()  # comment this line and AddressSanitizer will not complain
