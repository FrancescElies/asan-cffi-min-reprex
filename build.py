import subprocess

def run(*args, **kwargs):
    print(args[0])
    subprocess.run(*args, **kwargs, shell=True, check=True)
    print("\n\n")

clang_flags = ("-std=c99",
               "--target=x86_64-pc-windows-msvc",
               "-fuse-ld=lld",
               "-Wall",
               "-Wextra",
               "-Weverything",
               "-Werror",
               "-pedantic-errors",
               "-Wno-cast-align",
               "-fcomment-block-commands=retval",
               "-ferror-limit=200",
               "-fmessage-length=0",
               "-fno-short-enums",
               "-ffunction-sections",
               "-fdata-sections",
               "-g",
               "-gdwarf-4",
               "-O1",
               "-fno-omit-frame-pointer",
               "-fno-optimize-sibling-calls",
               )
with_asan = ("-shared-libsan", "-fsanitize=address")


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
