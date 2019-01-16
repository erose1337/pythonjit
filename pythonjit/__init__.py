"""Automatically cross compiles .py files to .so (or .pyd) using Cython and import hooks.

How to use:

    import pythonjit
    pythonjit.enable()

And imports will automatically be cythonized."""

try:
    import cython
except ImportError:
    print("Cython not installed")
    print("Run `pip install Cython` or `sudo pip install Cython` to get Cython")

import _cythonhook
import _compile
import compilepythonjit # necessary for auto-documentation

SHARED_LIBRARY = _compile.SHARED_LIBRARY
EXECUTABLE = _compile.EXECUTABLE

class Multiple_Enable_Error(Exception):
    """ Raised when pythonjit.enable is called when an Import_Hook already exists. """

class Not_Enabled_Error(Exception):
    """ Raised when pythonjit.disable is called when no Import_Hook exists. """

_STORAGE = []
def enable(verbosity=0, version='2'):
    """ usage: enable(verbosity=0, version='2') -> None

        Enables automatic cross compilation of imported python modules via Cython.
        This is the primary part of the API offered by the pythonjit package.

        verbosity is an optional keyword argument that can be set to:

            - 0 for no output
            - 1 for the beginning of compilation of a module to be output
            - 2 for the progress of the compilation process to be output, plus the output from 1

        version indicates the python version, and should be set to either '2' or '3'. Default is '2'.

        The Import_Hook created by calling enable() will live in the _STORAGE list in the pythonjit module.

        Calling enable when compilation is already enabled will raise Multiple_Enable_Error."""
    if any(_STORAGE):
        raise Multiple_Enable_Error("pythonjit.enable called when pythonjit already enabled")
    else:
        _STORAGE.append(_cythonhook.Import_Hook(version=version, verbosity=verbosity))

def disable():
    """ usage: disable() -> None

        Disables automatic compilation of imported python modules.
        Does not "uncompile" any previously compiled imported modules.
        enable can be called again to re-enable compilation of imported modules.

        Calling disable when compilation is not enabled will raise Not_Enabled_Error. """
    if not any(_STORAGE):
        raise Not_Enabled_Error("pythonjit.disable called when pythonjit not enabled")
    else:
        del _STORAGE[0]

def cross_compile(file_list, output_names, mode=SHARED_LIBRARY, version='2', verbosity=0):
    """ usage: cross_compile(file_list, output_names, mode=_compile.SHARED_LIBRARY,
                             version='2', verbosity=0) => list of compiled files

        Cross compiles the .py files specified in file_list to compiled binaries.
        file_list is a list of strings indicating the files to be converted, with the .py file extension
        output_names is a list of equivalent length of file_list, which specifies how the corresponding output files should be named. This argument is not optional, but None can be passed as entries to use the same names as those in the file_list (with a new file extension).
        mode is optional, and should be set to one of pythonjit._compile.SHARED_LIBRARY or pythonjit._compile.EXECUTABLE. Shared library type (.so, .pyd) is automatically determined by platform. Default is SHARED_LIBRARY
        version is optional, and should be a string set to either '2' or '3' to instruct cython that the correct python version is 2 or 3. Default is '2'
        verbosity is optional, and should be set to either 0 or 2; 0 is quiet mode with no output, while 2 provides step-by-step indication of the compilation process. verbosity=1 is reserved for the Import_Hook object. Default is 0

        example: cross_compile(["packagehead.py", "library.py"], [None, None],
                               mode=pythonjit.SHARED_LIBRARY, version='3', verbosity=2)"""
    return _compile.cross_compile(file_list, output_names, mode, version, verbosity)
