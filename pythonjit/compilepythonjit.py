import os

import _compile

def main(version=2, verbosity=2):
    this_file = __file__
    directory = os.path.split(this_file)[0]
    cythonhook_file = os.path.join(directory, "cythonhook.py")
    _compile_file = os.path.join(directory, "_compile.py")
    _database_file = os.path.join(directory, "_dabase.py")
    init_file = os.path.join(directory, "__init__.py")
    file_list = [init_file, _compile_file, cythonhook_file,
                 _database_file, this_file]
    _compile.cross_compile(file_list, [None] * len(file_list),
                           version=2, verbosity=verbosity)

if __name__ == "__main__":
    main()
