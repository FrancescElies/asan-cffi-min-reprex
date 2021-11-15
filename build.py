import sys
import os
from cffi.recompiler import make_c_source
import re
import subprocess
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Iterable, Optional

import cffi

repo = Path(__file__).absolute().parent

@contextmanager
def cwd(path):
    oldpwd=os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def run(*args, **kwargs):
    print(args[0])
    subprocess.run(*args, **kwargs, shell=True, check=True)
    print("\n\n")


def dumpbin(path: Path, imports=False, exports=False, symbols=False):
    dumpbin_exe = (r"C:\Program Files (x86)\Microsoft Visual Studio\2019"
                    r"\Professional\VC\Tools\MSVC\14.29.30133\bin\HostX86\x86"
                    r"\dumpbin.exe" )

    assert any((imports, exports, symbols))

    if exports:
        subprocess.run(rf'"{dumpbin_exe}" /exports "{path.absolute()}"')

    if imports:
        subprocess.run(rf'"{dumpbin_exe}" /imports "{path.absolute()}"')

    if symbols:
        subprocess.run(rf'"{dumpbin_exe}" /symbols "{path.absolute()}"')

def llvm_nm(path: Path):
    """ OVERVIEW: llvm symbol table dumper """
    subprocess.run(rf'llvm-nm "{path.absolute()}"')


clang_flags = (
    "-std=c99",
    "--target=x86_64-pc-windows-msvc",
    "-fuse-ld=lld",
    "-Wno-cast-align",
    "-fcomment-block-commands=retval",
    "-ferror-limit=200",
    "-fmessage-length=0",
    "-fno-short-enums",
    "-ffunction-sections",
    "-fdata-sections",
    "-O1",
    "-fno-omit-frame-pointer",
    "-fno-optimize-sibling-calls",
)

with_asan = ("-shared-libsan", "-fsanitize=address")


def cleanCDEF(cdef: str):
    cdef = cdef.replace("__declspec( dllexport )", "")
    return cdef


def load_ffi():
    ffiPath = repo / "c_src/ffi.i"
    ffi = cffi.FFI()
    clean_ffi = (repo / "c_src/clean_ffi.i")
    clean_ffi.write_text(cleanCDEF(ffiPath.read_text()))
    ffi.cdef(clean_ffi.read_text())
    return ffi


def build_pyd_msvc():
    ffi = load_ffi()

    with cwd(repo / "c_src"):
        ffi.set_source(
        module_name="_example",  # name of the output C extension
        source="""
        // passed to the real C compiler,
        // contains implementation of things declared in cdef()
        #include "example.h"   // the C header of the library
        """,
        sources=['example.c'],   # includes as additional sources
        libraries=[]
        )

    ffi.compile(verbose=True)


def build_pyd_clang_asan():
    r"""
    Compiles a pyd (dll) with clang and cffi in API Mode

    Tries to do the same as msvc but with clang as ffi.compile which makes the following calls

       C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe /c /nologo /Ox /W3 /GL /DNDEBUG /MD -Ic:\s\asan-cffi-min-reprex\venv\include -IC:\Python39\include -IC:\Python39\include -IC:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\ATLMFC\include -IC:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\include -IC:\Program Files (x86)\Windows Kits\NETFXSDK\4.8\include\um -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\ucrt -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\shared -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\um -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\winrt -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\cppwinrt /Tccffi_example_dll.c /Fo.\Release\example_dll.obj

       C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\link.exe /nologo /INCREMENTAL:NO /LTCG /DLL /MANIFEST:EMBED,ID=2 /MANIFESTUAC:NO /LIBPATH:c:\s\asan-cffi-min-reprex\venv\libs /LIBPATH:C:\Python39\libs /LIBPATH:C:\Python39 /LIBPATH:c:\s\asan-cffi-min-reprex\venv\PCbuild\amd64 /LIBPATH:C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\ATLMFC\lib\x64 /LIBPATH:C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\lib\x64 /LIBPATH:C:\Program Files (x86)\Windows Kits\NETFXSDK\4.8\lib\um\x64 /LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.19041.0\ucrt\x64 /LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.19041.0\um\x64 example.lib /EXPORT:PyInit_cffi_example_dll .\Release\example_dll.obj /OUT:.\example_dll.cp39-win_amd64.pyd /IMPLIB:.\Release\example_dll.cp39-win_amd64.lib

    Docs https://cffi.readthedocs.io/en/latest/overview.html#api-mode-calling-the-c-standard-library
    """

    ffi = load_ffi()
    out_folder = repo / "c_src/pyd_clang_asan"
    with suppress(FileExistsError):
        out_folder.mkdir()

    module_name = "cffi_wrap"
    cffi_api_mode_c_file = (repo / (f"{out_folder}/{module_name}.c")).absolute()

    target_c_file = (repo / (f"{out_folder}/{module_name}.c")).absolute()
    updated_c_source = make_c_source(
        ffi, module_name=module_name,
        preamble="""
        // This C code needs to make the declarated functions, types
        // and globals available, so it is often just the "#include".
        // passed to the real C compiler,
        // contains implementation of things declared in cdef()
        #include "example.h"   // the C header of the library
        """,
        target_c_file=target_c_file, verbose=True)

    print("Clang version")
    run("clang -v")

    print(f"Compile object files")
    object_file = cffi_api_mode_c_file.absolute().parent / f"{cffi_api_mode_c_file.stem}.obj"
    run(" ".join(("clang",
                    " ".join(clang_flags),
                    " ".join(with_asan),
                    "-I c_src",
                    r"-I C:\Python39\include",
                    "-fvisibility=default",
                    f"-c example.c",
                    f"-o {out_folder}/example.obj")), cwd=repo / "c_src")

    run(" ".join(("clang",
                    " ".join(clang_flags),
                    " ".join(with_asan),
                    f'-I {repo / "c_src"}',
                    r"-I C:\Python39\include",
                    "-fvisibility=default",
                    f"-c {cffi_api_mode_c_file.absolute()}",
                    f"-o {object_file}")), cwd=repo / "c_src")


    # NOTE: hardcoded python and plaltform
    # dll_file = object_file.parent / f"{object_file.stem}.cp39-win_amd64.pyd"
    dll_file = object_file.parent / f"{object_file.stem}.pyd"

    print(f"Compile dll")


    run(" ".join(("clang",
                    " ".join(clang_flags),
                    " ".join(with_asan),
                    # f"-Wl,/ignore:longsections,/export:PyInit_{object_file.stem}",  # :(
                    f"-Wl,/ignore:longsections,/DEF:{object_file.stem}.def",  # :(
                    r"-I C:\Python39\libs",
                    r"-L C:\Python39\libs",
                    f"{object_file}",
                    f"example.obj",
                    "-shared",
                    "-v",
                    f"-o {dll_file}")), cwd=out_folder)

    return dll_file


def build_dll_clang():
    _build(out_folder=repo / "c_src/dll_clang")


def build_dll_clang_asan():
    _build(out_folder=repo / "c_src/dll_clang_asan", extra_flags=with_asan)


def _build(out_folder: Path,
           extra_flags: Optional[Iterable[str]] = None):

    extra_flags = extra_flags or ()

    run(" clang -I c_src -E c_src/example.h > c_src/ffi.i ")

    with suppress(FileExistsError):
        out_folder.mkdir()

    run(" ".join(("clang",
                    " ".join(clang_flags),
                    " ".join(extra_flags),
                    "-I c_src",
                    "-c c_src/example.c",
                    f"-o {out_folder}/example.o")))

    run(" ".join(("clang",
                    " ".join(clang_flags),
                    " ".join(extra_flags),
                    "-Wl,/ignore:longsections",
                    f"{out_folder}/example.o",
                    "-shared",
                    f"-o {out_folder}/example.dll")))

    run("ls", cwd=out_folder)


if __name__ == '__main__':
    build_dll_clang()
    build_dll_clang_asan()
    build_pyd_clang_asan()
