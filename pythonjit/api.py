VERSION = "1.0.0-beta.2"
LANGUAGE = "python"
PROJECT = "pythonjit"

API = {"pythonjit.enable" : {"arguments" : None,
                             "keywords" : {"version" : "str", "verbosity" : "int",
                                           "db_name" : "filename str",
                                           "code_dir" : "directory str",
                                           "ignore_compilation_failure" : "bool"},
                             "returns" : None,
                             "exceptions" : ("Multiple_Enable_Error", )},
       "pythonjit.disable" : {"arguments" : None,
                              "returns" : None,
                              "exceptions" : "Not_Enabled_Error"},
       "pythonjit.cross_compile" : {"arguments" : ("iterable of str", "iterable of str"),
                                    "keywords" : {"mode" : "str",
                                                  "version" : "str",
                                                  "verbosity" : "int",
                                                  "compile_command" : "str"},
                                    "returns" : ("list of str", ),
                                    "exceptions" : ("Pyx_Conversion_Error",
                                                    "Cython_Conversion_Error",
                                                    "Compilation_Error")},
        "pythonjit.get_file_path" : {"arguments" : ("str", ),
                                     "returns" : ("str", ),
                                     "exceptions" : ("Not_Enabled_Error", )}
      }
