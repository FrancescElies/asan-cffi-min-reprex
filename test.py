from pathlib import Path


from build import build_dll_clang, build_dll_clang_asan, load_ffi, dumpbin

__file__ = "c:/s/asan-cffi-min-reprex/test.py"
file_path = Path(__file__).absolute()
repo = file_path.parent


def test_msvc_cffi_api_mode():
    from build import build_pyd_msvc
    build_pyd_msvc()
    import c_src._example as example
    mystruct = example.ffi.new("mystruct *")
    print(mystruct)


def test_api_mode_asan():
    from build import build_pyd_clang_asan
    build_pyd_clang_asan()
    # dumpbin(Path(r"c:\s\eklang\DevOps\clang\bin\LLVM-13.0.0-win64\lib\site-packages\lldb\_lldb.pyd"), "exports")
    dll_path_dir = repo / "c_src/pyd_clang_asan"
    dumpbin (dll_path_dir / "cffi_wrap.pyd", "exports")
    import c_src.pyd_clang_asan.cffi_wrap as cffi_wrap
    mystruct = cffi_wrap.ffi.new("mystruct *")
    print(f'OK API mode asan: {mystruct}')


def test_abi_mode_asan():
    ffi = load_ffi()
    build_dll_clang_asan()
    dllPath = repo / "c_src/dll_clang_asan/example.dll"
    print(f"dlopen {dllPath}")
    C = ffi.dlopen(str(dllPath.absolute()))

    mystruct = ffi.new("mystruct *")
    print(f'OK ABI mode asan: {mystruct}')


def test_abi_mode():
    ffi = load_ffi()
    build_dll_clang()
    dllPath = repo / "c_src/dll_clang/example.dll"
    # dumpbin(dllPath, exports=True)
    print(f"dlopen {dllPath}")
    C = ffi.dlopen(str(dllPath.absolute()))

    mystruct = ffi.new("mystruct *")
    print(f'OK ABI mode: {mystruct}')


if __name__ == '__main__':

    # The following combination BOOM! :cry:
    # see test_ok.py that works, is the same but copy pasting the contents of the functions
    test_abi_mode()
    test_abi_mode_asan()

    # test_api_mode_asan()
