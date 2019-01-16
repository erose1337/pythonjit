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
def enable(verbosity=0):
    """ usage: enable(verbosity=0) -> None

        Enables automatic cross compilation of imported python modules via Cython.
        This is the primary part of the API offered by the pythonjit package.

        verbosity is an optional keyword argument that can be set to:

            - 0 for no output
            - 1 for the beginning of compilation of a module to be output
            - 2 for the progress of the compilation process to be output, plus the output from 1

        The Import_Hook created by calling enable() will live in the _STORAGE list in the pythonjit module.

        Calling enable when compilation is already enabled will raise Multiple_Enable_Error."""
    if any(_STORAGE):
        raise Multiple_Enable_Error("pythonjit.enable called when pythonjit already enabled")
    else:
        _STORAGE.append(_cythonhook.Import_Hook(verbosity=verbosity))

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

cross_compile = _compile.cross_compile
