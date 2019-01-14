import os
from sys import platform
import subprocess

__all__ = ("SHARED_LIBRARY", "EXECUTABLE", "cross_compile")

SHARED_LIBRARY = "pyd" if "win" in platform else "so"
EXECUTABLE = "exe"
COMPILE_COMMAND = "gcc {} -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o {}." if "win" in platform else "gcc {} -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o {}."
#gcc converted.c -IC:\Python27\include -LC:\Python27\libs\ -lpython27 -o converted.exe

def convert_to_pyx(file_list):
    new_names = []

    for filename in file_list:
        extension = os.path.splitext(filename)[-1]
        if extension == ".py":
            pyx_filename = filename + 'x'
        else:
            raise ValueError("Cannot convert non-.py file to .pyx '{}' ext {}".format(filename, extension))
        with open(filename, 'r') as py_file, open(pyx_filename, 'w') as pyx_file:
            pyx_file.truncate(0)
            pyx_file.write(py_file.read())
            pyx_file.flush()
            new_names.append(pyx_filename)
    return new_names

def convert_to_c(file_names, mode, version='2', verbosity=0):
    cross_compile = "cython {} --embed" if mode is 'exe' else "cython {}"
    cross_compile += " -{}".format(version)
    c_files = []

    for filename in file_names:
        command = cross_compile.format(filename)
        error_code = os.system(command)
        assert filename[-3:] == 'pyx'
        os.remove(filename)
        if error_code > 0:
            raise ValueError("Failed to process '{}'".format(filename))
        else:
            c_file =  os.path.splitext(filename)[0] + '.c'
            c_files.append(c_file)
            if verbosity > 1:
                print "{} cross compiled successfully to {}".format(filename, c_file)
    return c_files

def ccompile(file_list, output_names, mode=SHARED_LIBRARY, verbosity=0):
    if len(file_list) != len(output_names):
        raise ValueError("file_list ({}) and output_names ({}) must be same length".format(len(file_list), len(output_names)))

    compile_mode = (mode + " -shared") if mode in ('pyd', 'so') else mode
    compile_command = COMPILE_COMMAND + compile_mode

    compiled = []
    for filename, output_filename in zip(file_list, output_names):
        if verbosity > 1:
            print("Compiling: {}".format(filename))
        if output_filename is None:
            output_filename = os.path.splitext(filename)[0]

        error_code = os.system(compile_command.format(filename, output_filename))
        assert filename[-1] == 'c'
        os.remove(filename)
        if error_code > 0:
            raise ValueError("Failed to compile '{}'".format(filename))
        else:
            if verbosity > 1:
                print "{} was compiled successfully".format(filename)
            compiled.append(output_filename)
    return compiled

def pyx_to_compiled(file_list, output_names, mode, version, verbosity):
    c_files = convert_to_c(file_list, mode)
    return ccompile(c_files, output_names, mode, verbosity)

def cross_compile(file_list, output_names, mode=SHARED_LIBRARY, version='2', verbosity=0):
    pyx_files = convert_to_pyx(file_list)
    return pyx_to_compiled(pyx_files, output_names, mode, version, verbosity)
