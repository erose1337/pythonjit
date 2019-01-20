""" This utility file can be used to cross-compile the code that performs cross-compilation.

Running `python compilepythonjit.py` will cross compile `__init__.py`, `_compile.py`, `_cythonhook.py`, `_database.py`, and `compilepythonjit.py`.

The python version defaults to python 2.

verbosity defaults to 2, which will display what/when files are being cross compiled."""

import os

import _compile

def main(version=2, verbosity=2):
    """ usage: main(version=2, verbosity=2) => None

        Cross compiles pythonjits source files to compiled binaries. """
    this_file = __file__
    directory = os.path.split(this_file)[0]
    cythonhook_file = os.path.join(directory, "_cythonhook.py")
    _compile_file = os.path.join(directory, "_compile.py")
    _database_file = os.path.join(directory, "_database.py")
    init_file = os.path.join(directory, "__init__.py")
    compile_file = os.path.join(directory, "compile.py")
    file_list = [init_file, _compile_file, cythonhook_file,
                 _database_file, this_file, compile_file]
    _compile.cross_compile(file_list, [None] * len(file_list),
                           version=2, verbosity=verbosity)

if __name__ == "__main__":
    main()
