""" Provides a [module finder](https://www.python.org/dev/peps/pep-0302/) class.

This is not a public facing module; Users of pythonjit should use `pythonjit.enable` to automatically compile imported modules, or use the `compile.py` program or `pythonjit.cross_compile` function to compile modules without importing them in python (e.g. in order to distribute them).

The `Import_Hook` class inserts itself into `sys.meta_path` when instantiated. When `import` statements are used, `Import_Hook` has the opportunity to locate the file to be imported. It uses this opportunity to locate the .py source code file for the module (if available), and uses `_compile.cross_compile` to compile it to a static library.

After that, its job is done; It passes the responsibility to find and load modules to the next or default finder/loader. That finder/loader will find the compiled version of the imported module, which will be used instead of the source code version of the module."""
import imp
import sys
import hashlib
import os
import errno

import pythonjit._compile
import pythonjit._database

__all__ = ["Import_Hook", "DEFAULT_DB"]

DEFAULT_DB =  os.path.join(os.path.expanduser("~"), "pythonjit", "cache.db")
CODE_DIR = os.path.join(os.path.expanduser("~"), "pythonjit", "compiled")

class Import_Hook(object):
    """ This object is instantiated when pythonjit.enable is called, and inserts itself into `sys.meta_path` as the first entry when instantiated.

        When a module is imported, this object is tasked with finding the module. This object will find the source code for the module, and cross compile it if necessary.

        This object does not participate in the module loading part of the import process. After the source file is cross compiled, it is left to other finders/loaders to load. The default loader will opt to load a compiled .so/.pyd over a .py file if it is available"""

    def __init__(self, version=2, verbosity=0, database_name=DEFAULT_DB, code_dir=CODE_DIR):
        if str(version) not in ('2', '3'):
            raise ValueError("Invalid version {}".format(version))
        sys.meta_path.insert(0, self)
        self.version = version
        self.verbosity = verbosity
        self.library_type = pythonjit._compile.SHARED_LIBRARY
        self.database = pythonjit._database.Cache_Database(database_name=database_name)
        self.code_dir = code_dir

    def find_module(self, module_name, path):
        """ Finds the specified module and cross compiles it if necessary.

            Uses a database to determine when source files change to determine whether the binaries should be re-compiled. """
        if module_name in sys.builtin_module_names:
            return None

        modules = module_name.split('.')
        end_of_modules = len(modules) - 1
        for count, module in enumerate(modules):
            try:
                _file, _path, description = imp.find_module(module, path)
            except ImportError:
                pass
            else:
                compiled_file = self.find_compiled_file(_path, module)
                if compiled_file is not None:
                    compiled_library_exists = True
                else:
                    compiled_library_exists = False

                _path = self.find_source_file(_path)
                if _path is None:
                    continue

                old_digest = self.database.query("Source_Info", retrieve_fields=("source_digest", ),
                                                 where={"module_name" : module_name})
                try_compiling = False
                if self.verbosity > 1:
                    print("Checking digest for {}".format(module_name))
                if old_digest:
                    source_digest = self.obtain_source_digest(_path)
                    if source_digest != old_digest:
                        if self.verbosity > 1:
                            print("Digest mismatch, code changed")
                        try_compiling = True
                    elif self.verbosity > 1:
                        print("Digests match")
                else:
                    if self.verbosity > 1:
                        print("Old digest not found")
                    try_compiling = True
                    source_digest = self.obtain_source_digest(_path)
                if not compiled_library_exists:
                    if self.verbosity > 1:
                        print("Compiled version does not exist yet")
                    try_compiling = True

                if count == end_of_modules and try_compiling:
                    if self.verbosity:
                        print("Cross compiling: {}".format(module_name))
                    self.cross_compile(_path)
                    self.update_db(module_name, source_digest, old_digest, _path)

    def obtain_source_digest(self, _path):
        """ Returns a hash of the file indicated by _path """
        with open(_path, 'r') as py_file:
            source = py_file.read()
        return hashlib.sha256(source).hexdigest()

    def update_db(self, module_name, source_digest, old_digest, path):
        """ Updates database with the hash of the source code """
        if old_digest:
            if self.verbosity > 1:
                print("Updating table with source_digest for {}".format(module_name))
            self.database.update_table("Source_Info", where={"module_name" : module_name},
                                       arguments={"source_digest" : source_digest,
                                                  "source_file" : path})
        else:
            if self.verbosity > 1:
                print("Inserting digest into db for {}".format(module_name))
            self.database.insert_into("Source_Info", values=(module_name,
                                                             source_digest,
                                                             path))

    def find_source_file(self, _path):
        """ Finds a source file for the file indacted by _path.

            _path may be to a .pyc/.so/.pyd or to a .py file.

            In the former case, the .py file is located and returned if available.
            Otherwise, simply returns the same _path that was supplied."""
        file_name, extension = os.path.splitext(_path)
        if extension != ".py":
            if not extension: # (sub)package, look for the __init__.py file
                file_name = os.path.join(file_name, "__init__.py")
            else:
                file_name = '.'.join((file_name, "py"))
            if not os.path.isfile(file_name):
                return None # can't find source, can't cross compile
            _path = file_name
        return _path

    def find_compiled_file(self, _path, module):
        """ Finds a compiled file for the file indicated by _path. """
        __path = os.path.splitext(os.path.sep.join((self.code_dir, _path[1:])))[0]
        try:
            _file, filepath, _ = imp.find_module(module, [__path])
        except ImportError:
            if os.path.split(__path)[-1] == module:
                filepath = os.path.join(__path, "__init__.so")
            else:
                return None
        else:
            _file.close()
        return filepath

    def cross_compile(self, _path):
        """ Cross compiles the python file indicated by _path into a binary. """
        assert _path[0] == os.path.sep
        output_path = os.path.splitext(os.path.sep.join((self.code_dir, _path[1:])))[0]
        directory = os.path.join(*os.path.split(output_path)[:-1])
        try:
            os.makedirs(directory)
        except OSError as error:
            if error.errno != errno.EEXIST or not os.path.isdir(directory):
                raise
        try:
            compiled = pythonjit._compile.cross_compile([_path], output_names=[output_path],
                                                        version=self.version,
                                                        verbosity=self.verbosity)
        except IOError as exception:
            if exception.errno != 13: # 13 = permission denied, probably in /usr/lib
                raise           # what about modules that have been `pip install`-ed?
                                # to do: Make sure only built-in modules don't get compiled
