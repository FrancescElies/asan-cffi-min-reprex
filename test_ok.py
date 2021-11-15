
from build import build_dll_clang, build_dll_clang_asan, load_ffi

if __name__ == '__main__':

    # this is like test.py but copy pasting the content of the functions.
    # Why does this work?

    ffi = load_ffi()
    build_dll_clang()
    dllPath = repo / "c_src/dll_clang/example.dll"
    # dumpbin(dllPath, exports=True)
    print(f"dlopen {dllPath}")
    C = ffi.dlopen(str(dllPath.absolute()))

    mystruct = ffi.new("mystruct *")
    print(f'OK ABI mode: {mystruct}')

    ffi = load_ffi()
    build_dll_clang_asan()
    dllPath = repo / "c_src/dll_clang_asan/example.dll"
    print(f"dlopen {dllPath}")
    C = ffi.dlopen(str(dllPath.absolute()))

    mystruct = ffi.new("mystruct *")
    print(f'OK ABI mode asan: {mystruct}')
