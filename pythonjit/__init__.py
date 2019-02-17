"""Automatically cross compiles .py files to .so (or .pyd) using Cython and import hooks.

How to use:

    import pythonjit
    pythonjit.enable()

And imports will automatically be cythonized."""
import sys
import os

try:
    import cython
except ImportError:
    print("Cython not installed")
    print("Run `pip install Cython` or `sudo pip install Cython` to get Cython")
    raise

import _cythonhook
import _compile
import _localimporter
import compilepythonjit # necessary for auto-documentation

SHARED_LIBRARY = _compile.SHARED_LIBRARY
EXECUTABLE = _compile.EXECUTABLE
CODE_DIR = os.path.join(os.path.expanduser("~"), "pythonjit", "compiled")

class Multiple_Enable_Error(Exception):
    """ Raised when pythonjit.enable is called when an Import_Hook already exists. """

class Not_Enabled_Error(Exception):
    """ Raised when pythonjit.disable is called when no Import_Hook exists.
        Also raised when functionality that requires Import_Hook is used when it does not exist. """

class Not_Compiled_Error(Exception):
    """ Raised when code that should be compiled is found to be interpreted instead. """

_STORAGE = []
def enable(verbosity=0, version='2', db_name=_cythonhook.DEFAULT_DB,
           code_dir=CODE_DIR, ignore_compilation_failure=False):
    """ usage: enable(verbosity=0, version='2', db_name=_cythonhook.DEFAULT_DB,
                      code_dir=CODE_DIR, ignore_compilation_failure=False) -> None

        Enables automatic cross compilation of imported python modules via Cython.
        This is the primary part of the API offered by the pythonjit package.

        verbosity is an optional keyword argument that can be set to:

            - 0 for no output
            - 1 for the beginning of compilation of a module to be output
            - 2 for the progress of the compilation process to be output, plus the output from 1

        version indicates the python version, and should be set to either '2' or '3'. Default is '2'.
        db_name is a filename string for the .db file that tracks when source code changes
        code_dir is a directory string that indicates where to cache compiled files
        ignore_compilation_failure is a boolean that indicates whether to use a regular interpreted python module if a module cannot be compiled

        The Import_Hook created by calling enable() will live in the _STORAGE list in the pythonjit module.

        Calling enable when compilation is already enabled will raise Multiple_Enable_Error."""
    if any(_STORAGE):
        raise Multiple_Enable_Error("pythonjit.enable called when pythonjit already enabled")
    else:
        _STORAGE.append(_cythonhook.Import_Hook(version=version, verbosity=verbosity,
                                                database_name=db_name, code_dir=code_dir,
                                                ignore_compilation_failure=ignore_compilation_failure))
        _STORAGE.append(_localimporter.Local_Importer(code_dir))

def disable():
    """ usage: disable() -> None

        Disables automatic compilation of imported python modules.
        Does not "uncompile" any previously compiled imported modules.
        enable can be called again to re-enable compilation of imported modules.

        Calling disable when compilation is not enabled will raise Not_Enabled_Error. """
    if not any(_STORAGE):
        raise Not_Enabled_Error("pythonjit.disable called when pythonjit not enabled")
    else:
        for item in _STORAGE:
            sys.meta_path.remove(item)
        del _STORAGE[:]

def cross_compile(file_list, output_names, mode=SHARED_LIBRARY, version='2', verbosity=0,
                  compile_command=_compile.COMPILE_COMMAND):
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
    return _compile.cross_compile(file_list, output_names, mode, version, verbosity, compile_command)

def get_file_path(module_name):
    """ usage: get_file_path(module_name) => file_path

    Facilitates access to __file__ information, which may be otherwise unavailable in compiled modules.

    module_name is a string of the modules name, e.g. as acquired by __name__.
    file_path is a string.

    Raises Not_Enabled_Error if pythonjit.enable has not been called yet."""
    if not _STORAGE:
        raise Not_Enabled_Error("Must enable pythonjit before db can be accessed")
    db = _STORAGE[0].database
    return db.query("Source_Info", retrieve_fields=("source_file", ),
                                   where={"module_name" : module_name}) or ''

# it would be nice to alias the requisite functionality from cython so that cython does not need to be imported
# would need to also alias cythons types to use these, otherwise you'd have to import cython anyways
#declare = cython.declare
#cclass = cython.cclass
#cfunc = cython.cfunc
#ccall = cython.ccall
#locals = cython.locals
#returns = cython.returns
#inline = cython.inline
#final = cython.final
