import re
import unittest
from pathlib import Path

import cffi
from cffi.recompiler import make_c_source

from build import build

file_path = Path(__file__).absolute()
file_directory = file_path.parent


def cleanCDEF(cdef: str):
  cdef = cdef.replace("__declspec( dllexport )", "")
  return cdef

def load_ffi():
  ffiPath = file_directory / "c_src/ffi.i"
  ffi = cffi.FFI()
  clean_ffi = (file_directory / "c_src/clean_ffi.i")
  clean_ffi.write_text(cleanCDEF(ffiPath.read_text()))
  ffi.cdef(clean_ffi.read_text())
  return ffi


def load_dll_cffi_api_mode(ffi):
  # This C code needs to make the declarated functions, types
  # and globals available, so it is often just the "#include".
  preamble = """
  // passed to the real C compiler,
  // contains implementation of things declared in cdef()
  #include "example.h"   // the C header of the library
  """
  cffi_api_mode_c_file = (file_directory / ("c_src/cffi_example_dll.c")).absolute()
  updated_c_source = make_c_source(
    ffi, module_name="cffi_example_dll", preamble=preamble,
    target_c_file=cffi_api_mode_c_file, verbose=True)

  from build import build_cffi_api_mode
  dll_file = build_cffi_api_mode(cffi_api_mode_c_file)
  return dll_file


def test_example(asan_cffi_api_mode=False, no_asan=False, asan=False):
  ffi = load_ffi()

  dllPath = None

  if asan_cffi_api_mode:
    dllPath = load_dll_cffi_api_mode(ffi)

  if asan:
    dllPath = file_directory / "c_src/asanexample.dll"

  if no_asan:
    dllPath = file_directory / "c_src/example.dll"

  assert dllPath

  print(f"dlopen {dllPath}")
  C = ffi.dlopen(str(dllPath.absolute()))

  mystruct = ffi.new("mystruct *")


class Mytest(unittest.TestCase):
  def dummy_test(self):
    ...


if __name__ == '__main__':
  build()


  # This seems ok, but not sure
  test_example(no_asan=True)
  test_example(asan=True)
  # test_example(asan_cffi_api_mode=True)

  # unittest explodes BOOM
  unittest.main()  # comment this line and AddressSanitizer will not complain
