""" Handles the process of using cython and gcc to cross compile .py files into .pyx, then into .c, then into .so/.pyd/.exe.

While this module does expose one function that is intended to be available to end users, that function is aliased in the `pythonjit` module.

This module is not part of the exposed API, and users should access the `cross_compile` functionality through `pythonjit`."""
import os
from sys import platform
import tempfile

__all__ = ("SHARED_LIBRARY", "EXECUTABLE", "cross_compile")

SHARED_LIBRARY = "pyd" if "win" in platform else "so"
EXECUTABLE = "exe"
COMPILE_COMMAND = "gcc {} -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o {}." if "win" in platform else "gcc {} -pthread -fPIC -fwrapv -O2 -fno-strict-aliasing -I /usr/include/python2.7 -lpython2.7 -lpthread -lm -lutil -ldl -o {}."

class Compilation_Error(Exception):
    """ Raised when a compiler (e.g. gcc) fails to compile a .c file. """

class Cython_Conversion_Error(Exception):
    """ Raised when cython fails to compile a .pyx file. """

class Pyx_Conversion_Error(Exception):
    """ Raised when convert_to_pyx is supplied a non-.py file. """


def convert_to_pyx(file_list):
    """ usage: convert_to_pyx(file_list) => list of .pyx file names

        creates .pyx files from a list of .py files.
        file_list should be a list of strings of python source files.

        The "conversion" process consists of making a copy of the supplied file with a .pyx file extension."""
    pyx_files = []
    for filename in file_list:
        extension = os.path.splitext(filename)[-1]
        if extension != ".py":
            raise Pyx_Conversion_Error("Cannot convert non-.py file to .pyx '{}' ext {}".format(filename, extension))
        with open(filename, 'r') as py_file:#, open(pyx_filename, 'w') as pyx_file:
            pyx_file = tempfile.NamedTemporaryFile(suffix=".pyx")
            pyx_file.write(py_file.read())
            pyx_file.flush()
            pyx_files.append((filename, pyx_file))
    return pyx_files

def convert_to_c(pyx_files, mode, version='2', verbosity=0):
    """ usage: convert_to_c(file_names, mode, version='2', verbosity=0) => list of .c file names

        Converts .pyx files to .c files via cython.
        file_names should be a list of strings of .pyx file names
        mode should be SHARED_LIBRARY or EXECUTABLE
        version should be either '2' or '3' for python 2 or 3. Defaults to '2'.
        verbosity should be 0 or 2. 0 is silent, 2 prints filenames as they are converted. Defaults to 0."""
    cross_compile = "cython {} --embed" if mode == 'exe' else "cython {}"
    cross_compile += " -{}".format(version)
    c_files = []

    for py_filename, pyx_file in pyx_files:
        filename = pyx_file.name
        command = cross_compile.format(pyx_file.name)
        error_code = os.system(command)
        assert filename[-3:] == 'pyx'
        pyx_file.close() # deletes temporary file
        if error_code > 0:
            c_file = os.path.splitext(filename)[0] + ".c"
            os.remove(c_file)
            raise Cython_Conversion_Error("Failed to process '{}'".format(py_filename))
        else:
            c_file =  os.path.splitext(filename)[0] + '.c'
            c_files.append((py_filename, c_file))
            if verbosity > 1:
                print "{} cross compiled successfully to {}".format(py_filename, c_file)
    return c_files

def ccompile(file_list, output_names, mode=SHARED_LIBRARY, verbosity=0,
             compile_command=COMPILE_COMMAND):
    """ usage: ccompile(file_list, output_names, mode=SHARED_LIBRARY, verbosity=0,
                        compile_command=COMPILE_COMMAND) => list of file names

        Compiles .c files into .so/.pyd/.exe files via `gcc`.
        file_list should be a list of .c file names
        output_names should be a list of file names, or a list of None of the same length as file_list to name the compiled files after the .c files.
        mode should be set to SHARED_LIBRARY or EXECUTABLE to compile. Defaults to SHARED_LIBRARY
        verbosity should be set to 0 or 2. 0 is silent, 2 prints filenames as they are compiled. Defaults to 0.
        compile_command is the command string to invoke gcc. Defaults to COMPILE_COMMAND. Alternative command strings should accept two format insertions for the source/output file names. The source file that is inserted will include the .c file extension, while the output file that is inserted must not, as it is dynamically determined by the program."""

    if len(file_list) != len(output_names):
        raise ValueError("file_list ({}) and output_names ({}) must be same length".format(len(file_list), len(output_names)))

    compile_mode = (mode + " -shared") if mode in ('pyd', 'so') else mode
    compile_command = compile_command + compile_mode

    compiled = []
    for filenames, output_filename in zip(file_list, output_names):
        py_filename, filename = filenames
        if verbosity > 1:
            print("Compiling: {} ({})".format(filename, py_filename))
        if output_filename is None:
            output_filename = os.path.splitext(filename)[0]

        error_code = os.system(compile_command.format(filename, output_filename))
        assert filename[-1] == 'c'
        os.remove(filename)
        if error_code > 0:
            raise Compilation_Error("Failed to compile '{}'".format(py_filename))
        else:
            if verbosity > 1:
                print "{} was compiled successfully".format(py_filename)
            compiled.append("{}.{}".format(output_filename, mode))
    return compiled

def cross_compile(file_list, output_names, mode=SHARED_LIBRARY, version='2', verbosity=0,
                  compile_command=COMPILE_COMMAND):
    """ usage: cross_compile(file_list, output_names, mode=_compile.SHARED_LIBRARY,
                             version='2', verbosity=0
                             compile_command=_compile.COMPILE_COMMAND) => list of compiled file names

        Cross compiles the .py files specified in file_list to compiled binaries.
        file_list is a list of strings indicating the files to be converted, with the .py file extension
        output_names is a list of equivalent length of file_list, which specifies how the corresponding output files should be named. This argument is not optional, but None can be passed as entries to use the same names as those in the file_list (with a new file extension).
        mode is optional, and should be set to one of pythonjit._compile.SHARED_LIBRARY or pythonjit._compile.EXECUTABLE. Shared library type (.so, .pyd) is automatically determined by platform. Default is SHARED_LIBRARY
        version is optional, and should be a string set to either '2' or '3' to instruct cython that the correct python version is 2 or 3. Default is '2'
        verbosity is optional, and should be set to either 0 or 2; 0 is quiet mode with no output, while 2 provides step-by-step indication of the compilation process. verbosity=1 is reserved for the Import_Hook object. Default is 0
        compile_command is optional, and should be set to a string with 2 format/insertion points that runs a compiler (e.g. gcc) with any relevant flags/switches. The first insertion should be for the file name (something.c), and the second insertion point should be for the executable/library name, *without* the file extension (that will be inserted automatically)

        examples:

            cross_compile(["packagehead.py", "library.py"], [None, None],
                          mode=pythonjit.SHARED_LIBRARY, version='3', verbosity=2)

            cross_compile(["main.py"], ["myapp"], mode=pythonjit.EXECUTABLE)"""
    pyx_files = convert_to_pyx(file_list)
    c_files = convert_to_c(pyx_files, mode, version, verbosity)
    return ccompile(c_files, output_names, mode, verbosity)
