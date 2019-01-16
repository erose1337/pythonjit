pythonjit._compile
==============

 Handles the process of using cython and gcc to cross compile .py files into .pyx, then into .c, then into .so/.pyd/.exe.

While this module does expose one function that is intended to be available to end users, that function is aliased in the `pythonjit` module.

This module is not part of the exposed API, and users should access the `cross_compile` functionality through `pythonjit`.

ccompile
--------------

**ccompile**(file_list, output_names, mode, verbosity, compile_command):

		 usage: ccompile(file_list, output_names, mode=SHARED_LIBRARY, verbosity=0,
                        compile_command=COMPILE_COMMAND) => list of file names

        Compiles .c files into .so/.pyd/.exe files via `gcc`.
        file_list should be a list of .c file names
        output_names should be a list of file names, or a list of None of the same length as file_list to name the compiled files after the .c files.
        mode should be set to SHARED_LIBRARY or EXECUTABLE to compile. Defaults to SHARED_LIBRARY
        verbosity should be set to 0 or 2. 0 is silent, 2 prints filenames as they are compiled. Defaults to 0.
        compile_command is the command string to invoke gcc. Defaults to COMPILE_COMMAND. Alternative command strings should accept two format insertions for the source/output file names. The source file that is inserted will include the .c file extension, while the output file that is inserted must not, as it is dynamically determined by the program.


convert_to_c
--------------

**convert_to_c**(file_names, mode, version, verbosity):

		 usage: convert_to_c(file_names, mode, version='2', verbosity=0) => list of .c file names

        Converts .pyx files to .c files via cython.
        file_names should be a list of strings of .pyx file names
        mode should be SHARED_LIBRARY or EXECUTABLE
        version should be either '2' or '3' for python 2 or 3. Defaults to '2'.
        verbosity should be 0 or 2. 0 is silent, 2 prints filenames as they are converted. Defaults to 0.


convert_to_pyx
--------------

**convert_to_pyx**(file_list):

		 usage: convert_to_pyx(file_list) => list of .pyx file names

        creates .pyx files from a list of .py files.
        file_list should be a list of strings of python source files.

        The "conversion" process consists of making a copy of the supplied file with a .pyx file extension.


cross_compile
--------------

**cross_compile**(file_list, output_names, mode, version, verbosity):

		 usage: cross_compile(file_list, output_names, mode=_compile.SHARED_LIBRARY,
                             version='2', verbosity=0) => list of compiled files

        Cross compiles the .py files specified in file_list to compiled binaries.
        file_list is a list of strings indicating the files to be converted, with the .py file extension
        output_names is a list of equivalent length of file_list, which specifies how the corresponding output files should be named. This argument is not optional, but None can be passed as entries to use the same names as those in the file_list (with a new file extension).
        mode is optional, and should be set to one of pythonjit._compile.SHARED_LIBRARY or pythonjit._compile.EXECUTABLE. Shared library type (.so, .pyd) is automatically determined by platform. Default is SHARED_LIBRARY
        version is optional, and should be a string set to either '2' or '3' to instruct cython that the correct python version is 2 or 3. Default is '2'
        verbosity is optional, and should be set to either 0 or 2; 0 is quiet mode with no output, while 2 provides step-by-step indication of the compilation process. verbosity=1 is reserved for the Import_Hook object. Default is 0

        example: cross_compile(["packagehead.py", "library.py"], [None, None],
                               mode=pythonjit.SHARED_LIBRARY, version='3', verbosity=2)
