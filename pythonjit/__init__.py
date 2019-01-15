""" Automatically cross compiles .py files to .so (or .pyd) using Cython and import hooks.

    How to use:

        import pythonjit
        pythonjit.enable()

    And imports will automatically be cythonized.

    For more performance benefits, use the decorators provided by cython to statically type variables and return types.
    The relevant decorators are:

        - @cython.cfunc (declares cdef function)
        - @cython.ccall (declares cpdef function)
        - @cython.returns (declare return type)
        - @cython.locals (declare local variable types)
        - @cython.cclass (declare cdef class)
        - @cython.inline (equivalent to C inline keyword)
        - @cython.final (makes subclassing impossible, enabling optimizations)

    Types are also part of the cython module:

        - cython.int
        - cython.longlong
        - cython.struct
        - cython.union
        - cython.typedef
        - cython.cast
        - etc

    For more information on cython types and decorators, see the [cython docs](http://docs.cython.org/en/latest/src/tutorial/pure.html#static-typing)

    Cython is more stringent than the python interpreter when it comes to catching errors in code.
    E.g. It will complain about NameErrors that occur in unreachable code, which the python interpreter will not do.
    A larger/complex project may have issues to fix before Cython can compile it.

    Cross compilation can take some time, especially for larger projects.
    A caching mechanism is used to compensate for this, so the first run will be slower than future runs.

    Notes/Known issues/Complications:

        __file__ may not be available in compiled modules - see https://stackoverflow.com/questions/19225188/what-method-can-i-use-instead-of-file-in-python#comment65304373_19225368 for a workaround"""
try:
    import cython
except ImportError:
    print("Cython not installed")
    print("Run `pip install Cython` or `sudo pip install Cython` to get Cython")

from _cythonhook import Import_Hook
from _compile import *

class Multiple_Enable_Error(Exception):pass
class Not_Enabled_Error(Exception): pass

_STORAGE = []
def enable(verbosity=0):
    """ usage: enable(verbosity=0) -> None

        Enables automatic cross compilation of imported python modules via Cython.
        verbosity is an optional keyword argument that can be set to:

            - 0 for no output
            - 1 for the beginning of compilation of a module to be output
            - 2 for the progress of the compilation process to be output, plus the output from 1

        The Import_Hook created by calling enable() will live in the _STORAGE list in the pythonjit module.

        Calling enable when compilation is already enabled will raise Multiple_Enable_Error."""
    if any(_STORAGE):
        raise Multiple_Enable_Error("pythonjit.enable called when pythonjit already enabled")
    else:
        _STORAGE.append(Import_Hook(verbosity=verbosity))

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
    return _compile.cross_compile(file_list, output_names, mode, version, verbosity)
