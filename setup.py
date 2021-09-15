import cx_Freeze

executables = [cx_Freeze.Executable("demo.py")]

cx_Freeze.setup(
    name="rhythm_test",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":["ode_to_idle_gaming.otf",
                                            "img",
                                            "levels",
                                            "sfx"
                                            ]}},
    executables = executables

    )
