import imp
import sys
import hashlib
import os

import pythonjit._compile
import pythonjit.database

__all__ = ["Import_Hook"]

class Import_Hook(object):
    """ This object is automatically instantiated and inserted into
        sys.meta_path as the first entry when instantiated. """

    def __init__(self, version=2, verbosity=0, database_name="cache.db"):
        sys.meta_path.insert(0, self)
        self.version = version
        self.verbosity = verbosity
        self.database = pythonjit.database.Cache_Database(database_name=database_name)

    def find_module(self, module_name, path):
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
                if "/usr/lib" in _path: # possibly improper solution to compiling builtins
                    continue

                _path = self.find_source_file(_path)
                if _path is None:
                    continue

                old_digest = self.database.query("Source_Cache", retrieve_fields=("source_digest", ),
                                                 where={"module_name" : module_name})
                try_compiling = False
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

                if count == end_of_modules and try_compiling:
                    if self.verbosity:
                        print("Cross compiling: {}".format(module_name))
                    self.cross_compile(_path)
                    self.update_db(module_name, source_digest, old_digest)

    def obtain_source_digest(self, _path):
        with open(_path, 'r') as py_file:
            source = py_file.read()
        return hashlib.sha256(source).hexdigest()

    def update_db(self, module_name, source_digest, old_digest):
        if old_digest:
            if self.verbosity > 1:
                print("Updating table with source_digest for {}".format(module_name))
            self.database.update_table("Source_Cache", where={"module_name" : module_name},
                                       arguments={"source_digest" : source_digest})
        else:
            if self.verbosity > 1:
                print("Inserting digest into db for {}".format(module_name))
            self.database.insert_into("Source_Cache", values=(module_name, source_digest))

    def find_source_file(self, _path):
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

    def cross_compile(self, _path):
        try:
            compiled = pythonjit._compile.cross_compile([_path], output_names=[None],
                                                        version=self.version,
                                                        verbosity=self.verbosity)
        except IOError as exception:
            if exception.errno != 13: # 13 = permission denied, probably in /usr/lib
                raise           # what about modules that have been `pip install`-ed?
                                # to do: Make sure only built-in modules don't get compiled
