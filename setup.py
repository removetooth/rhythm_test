import cx_Freeze, sys, os

base = None
if (sys.platform == "win32"):
    base = "Win32GUI"

executables = [
    cx_Freeze.Executable(
        "main.py",
        base=base,
        target_name = "rhythm_test"
        )
    ]

cx_Freeze.setup(
    name="rhythm_test",
    options={"build_exe": {
        "packages":[
            "pygame",
            "OpenGL",
            "OpenGL.platform.win32",
            "OpenGL.arrays.numpymodule",
            "OpenGL.arrays.strings",
            "OpenGL.GLU",
            "OpenGL.GLU.glustruct"
            ],
        "optimize": 1,
        "include_files":[
           "ode_to_idle_gaming.otf",
            "img",
            "levels",
            "sfx"
            ],
        "excludes":[
           "asyncio",
           "concurrent",
           "curses",
           "distutils",
           "email",
           "html",
           "http",
           "lib2to3",
           #"logging",
           "msizxcclib",
           "multiprocessing",
           "pkg_resources",
           "pydoc_data",
           "setuptools",
           "test",
           "tkinter",
           "unittest",
           #"urllib",
           "xml",
           "xmlrpc",
           #"numpy",
           #"ctypes",
           "socket",
           "pygame.examples",
           "pygame.tests"
           ]
       }},
                        
    executables = executables

    )
