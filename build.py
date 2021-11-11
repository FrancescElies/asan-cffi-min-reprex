from pathlib import Path
import subprocess

def run(*args, **kwargs):
    print(args[0])
    subprocess.run(*args, **kwargs, shell=True, check=True)
    print("\n\n")

clang_flags = ("-std=c99",
               "--target=x86_64-pc-windows-msvc",
               "-fuse-ld=lld",
               "-Wno-cast-align",
               "-fcomment-block-commands=retval",
               "-ferror-limit=200",
               "-fmessage-length=0",
               "-fno-short-enums",
               "-ffunction-sections",
               "-fdata-sections",
               # debug symbos (-g)
               "-g",
               "-gdwarf-4",
               "-O1",
               "-fno-omit-frame-pointer",
               "-fno-optimize-sibling-calls",
               )
with_asan = ("-shared-libsan", "-fsanitize=address")


def build_cffi_api_mode(cffi_api_mode_c_file: Path):
    r"""
    Compiles a dll for cffi in API Mode

    Tries to do the same as msvc but with clang as ffi.compile which makes the following calls
       C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe /c /nologo /Ox /W3 /GL /DNDEBUG /MD -Ic:\s\asan-cffi-min-reprex\venv\include -IC:\Python39\include -IC:\Python39\include -IC:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\ATLMFC\include -IC:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\include -IC:\Program Files (x86)\Windows Kits\NETFXSDK\4.8\include\um -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\ucrt -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\shared -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\um -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\winrt -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\cppwinrt /Tccffi_example_dll.c /Fo.\Release\cffi_example_dll.obj
       C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\link.exe /nologo /INCREMENTAL:NO /LTCG /DLL /MANIFEST:EMBED,ID=2 /MANIFESTUAC:NO /LIBPATH:c:\s\asan-cffi-min-reprex\venv\libs /LIBPATH:C:\Python39\libs /LIBPATH:C:\Python39 /LIBPATH:c:\s\asan-cffi-min-reprex\venv\PCbuild\amd64 /LIBPATH:C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\ATLMFC\lib\x64 /LIBPATH:C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.29.30133\lib\x64 /LIBPATH:C:\Program Files (x86)\Windows Kits\NETFXSDK\4.8\lib\um\x64 /LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.19041.0\ucrt\x64 /LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.19041.0\um\x64 example.lib /EXPORT:PyInit_cffi_example_dll .\Release\cffi_example_dll.obj /OUT:.\cffi_example_dll.cp39-win_amd64.pyd /IMPLIB:.\Release\cffi_example_dll.cp39-win_amd64.lib

    Docs https://cffi.readthedocs.io/en/latest/overview.html#api-mode-calling-the-c-standard-library
    """
    print("Clang version")
    run("clang -v")

    print(f"Compile object files")
    object_file = cffi_api_mode_c_file.absolute().parent / f"{cffi_api_mode_c_file.stem}.obj"
    run(" ".join(("clang",
                    " ".join(clang_flags),
                    " ".join(with_asan),
                    "-I c_src",
                    r"-I C:\Python39\include",
                    f"-c {cffi_api_mode_c_file.absolute()}",
                    f"-o {object_file}")))

    dll_file = object_file.parent / f"{object_file.stem}.dll"

    print(f"Compile dll")
    run(" ".join(("clang",
                    " ".join(clang_flags),
                    " ".join(with_asan),
                    "-Wl,/ignore:longsections",
                    r"-I C:\Python39\libs"
                    f"{object_file}",
                    "-shared",
                    f"-o {dll_file}")))
    return dll_file


def build():

    print("Clean previous compilation")
    run("git clean -fdx c_src")

    print("Clang version")
    run("clang -v")

    print("Compile ffi")
    run(" clang -I c_src -E c_src/example.h > c_src/ffi.i ")

    for (prefix, extra_flags) in zip(("asan", ""), (with_asan, ())):
        print(f"Compile object files {prefix}")
        run(" ".join(("clang",
                      " ".join(clang_flags),
                      " ".join(extra_flags),
                      "-I c_src",
                      "-c c_src/example.c",
                      f"-o c_src/{prefix}example.o")))

        print(f"Compile dll {prefix}")
        run(" ".join(("clang",
                      " ".join(clang_flags),
                      " ".join(extra_flags),
                      "-Wl,/ignore:longsections",
                      f"c_src/{prefix}example.o",
                      "-shared",
                      f"-o c_src/{prefix}example.dll")))


if __name__ == '__main__':
    build()
