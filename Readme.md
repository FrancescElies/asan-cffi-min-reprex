# Minimal, REPRoducible EXample (reprex) llvm-AddressSanitizer Python3.9 Cffi Unittest 

We have a complex project where we build a dll and we test it via cffi.
This dll is build for windows and this issue has been reproduced with.
 - clang version 12 or 13 (happens with both)
 - Python 3.9.6
 - cffi 1.15.0

## Setup
On windows install.

  - [llvm13](https://github.com/llvm/llvm-project/releases/download/llvmorg-13.0.0/LLVM-13.0.0-win64.exe)
  - [python 3.9.6](https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe)

And create a new virtual environment
```powershell
py -3.9 -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install cffi==1.15.0
```


## Test case
With the previously created venv active (.\venv\Scripts\activate)

Compiling a dll with asan and running `python test.py` 
<details><summary>👀 AddressSanitizer report (click me)</summary>
<p>

```
will explode with the a bad-free.
=================================================================
==1772==ERROR: AddressSanitizer: attempting free on address which was not malloc()-ed: 0x01f5b26220d0 in thread T0
    #0 0x7fff40b27f31  (C:\LLVM-13.0.0-win64\lib\clang\13.0.0\lib\windows\clang_rt.asan_dynamic-x86_64.dll+0x180037f31)
    #1 0x7fff5a0959ec in _PyObject_Realloc D:\_w\1\s\Objects\obmalloc.c:2011
    #2 0x7fff5a16f347 in _PyObject_GC_Resize D:\_w\1\s\Modules\gcmodule.c:2309
    #3 0x7fff5a0ceeaa in _PyEval_EvalCode D:\_w\1\s\Python\ceval.c:4101
    #4 0x7fff5a0cfa66 in _PyFunction_Vectorcall D:\_w\1\s\Objects\call.c:396
    #5 0x7fff5a0c57b4 in slot_tp_init D:\_w\1\s\Objects\typeobject.c:6943
    #6 0x7fff5a0c595c in type_call D:\_w\1\s\Objects\typeobject.c:1026
    #7 0x7fff5a124cbb in _PyObject_MakeTpCall D:\_w\1\s\Objects\call.c:191
    #8 0x7fff5a0d8663 in _PyEval_EvalFrameDefault D:\_w\1\s\Python\ceval.c:3535
    #9 0x7fff5a0d2774 in _PyEval_EvalFrameDefault D:\_w\1\s\Python\ceval.c:3504
    #10 0x7fff5a0d2774 in _PyEval_EvalFrameDefault D:\_w\1\s\Python\ceval.c:3504
    #11 0x7fff5a0d2774 in _PyEval_EvalFrameDefault D:\_w\1\s\Python\ceval.c:3504
    #12 0x7fff5a0ce0a2 in _PyEval_EvalCode D:\_w\1\s\Python\ceval.c:4327
    #13 0x7fff5a0cfa66 in _PyFunction_Vectorcall D:\_w\1\s\Objects\call.c:396
    #14 0x7fff5a0c55f0 in slot_tp_init D:\_w\1\s\Objects\typeobject.c:6943
    #15 0x7fff5a0c595c in type_call D:\_w\1\s\Objects\typeobject.c:1026
    #16 0x7fff5a0d4edd in _PyEval_EvalFrameDefault D:\_w\1\s\Python\ceval.c:3487
    #17 0x7fff5a0ce0a2 in _PyEval_EvalCode D:\_w\1\s\Python\ceval.c:4327
    #18 0x7fff5a1268fc in _PyEval_EvalCodeWithName D:\_w\1\s\Python\ceval.c:4359
    #19 0x7fff5a11e9d2 in PyEval_EvalCodeEx D:\_w\1\s\Python\ceval.c:4375
    #20 0x7fff5a11e930 in PyEval_EvalCode D:\_w\1\s\Python\ceval.c:826
    #21 0x7fff5a0ab671 in run_eval_code_obj D:\_w\1\s\Python\pythonrun.c:1219
    #22 0x7fff5a0ab5f1 in run_mod D:\_w\1\s\Python\pythonrun.c:1240
    #23 0x7fff5a162e46 in pyrun_file D:\_w\1\s\Python\pythonrun.c:1138
    #24 0x7fff5a1632ef in pyrun_simple_file D:\_w\1\s\Python\pythonrun.c:449
    #25 0x7fff5a16ebe6 in PyRun_SimpleFileExFlags D:\_w\1\s\Python\pythonrun.c:482
    #26 0x7fff5a16eb7f in PyRun_AnyFileExFlags D:\_w\1\s\Python\pythonrun.c:91
    #27 0x7fff5a16e915 in pymain_run_file D:\_w\1\s\Modules\main.c:373
    #28 0x7fff5a132347 in pymain_run_python D:\_w\1\s\Modules\main.c:598
    #29 0x7fff5a1321d0 in Py_RunMain D:\_w\1\s\Modules\main.c:677
    #30 0x7fff5a12e3f0 in Py_Main D:\_w\1\s\Modules\main.c:719
    #31 0x7ff6fd5d1253 in invoke_main d:\agent\_work\4\s\src\vctools\crt\vcstartup\src\startup\exe_common.inl:90
    #32 0x7ff6fd5d1253 in __scrt_common_main_seh d:\agent\_work\4\s\src\vctools\crt\vcstartup\src\startup\exe_common.inl:288
    #33 0x7fffd14d7c23  (C:\Windows\System32\KERNEL32.DLL+0x180017c23)
    #34 0x7fffd22cd720  (C:\Windows\SYSTEM32\ntdll.dll+0x18006d720)

Address 0x01f5b26220d0 is a wild pointer inside of access range of size 0x000000000001.
SUMMARY: AddressSanitizer: bad-free (C:\LLVM-13.0.0-win64\lib\clang\13.0.0\lib\windows\clang_rt.asan_dynamic-x86_64.dll+0x180037f31)
==1772==ABORTING
```

</p>
</details>

### Two interesting things:
Info: (1) and (2) are independent from each other.

#### Why calling unittest.main() crashes?
If you comment this line as follows

``` python
  # unittest.main()  # comment this line and AddressSanitizer will not complain
```

AddressSanitizer will not explode

#### Why having an array in the struct crashes?
Modify `c_src/example.h` as follows
```
  // mystruct_depth2 boom[2];   // comment this line and test.py will not make asan explode ¯\_(ツ)_/¯
  mystruct_depth2 boom;   // This is OK. Uncomment this line and comment the previous one and see. 
```
AddressSanitizer will not explode


## Suspects
- LLVM AddressSanitizer detecting the wrong thing?
- Python's garbage collector?
- Cffi freeing something it shouldn't?
- Something else?
