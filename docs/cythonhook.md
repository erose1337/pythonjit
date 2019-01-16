pythonjit._cythonhook
==============

 Provides a [module finder](https://www.python.org/dev/peps/pep-0302/) class.

This is not a public facing module; Users of pythonjit should use `pythonjit.enable` to automatically compile imported modules, or `pythonjit.cross_compile` as a utility to compile modules without importing them in python (e.g. in order to distribute them).

The `Import_Hook` class inserts itself into `sys.meta_path` when instantiated. When `import` statements are used, `Import_Hook` has the opportunity to locate the file to be imported. It uses this opportunity to locate the .py source code file for the module (if available), and uses `_compile.cross_compile` it to a static library.

After that, it's job is done; It passes the responsibility to find and load modules to the next or default finder/loader. That finder/loader will find the compiled version of the imported module, which will be used instead of the source code version of the module.

Import_Hook
--------------

This object is automatically instantiated and inserted into `sys.meta_path` as the first entry when instantiated.

When a module is imported, this object is tasked with finding the module. This object will find the source code for the module, and cross compile it if necessary.

This object does not participate in the module loading part of the import process. After the source file is cross compiled, it is left to the default/other finders/loaders to load. The default loader will opt to load a compiled .so/.pyd over a .py file if it is available


Method resolution order:

	(<class 'pythonjit._cythonhook.Import_Hook'>, <type 'object'>)

- **find_module**(self, module_name, path):

		Finds the specified module and cross compiles it if necessary.

        Uses a database to determine when source files change to determine whether the binaries should be re-compiled.


- **cross_compile**(self, _path):

		Cross compiles the python file indicated by _path into a binary.


- **update_db**(self, module_name, source_digest, old_digest):

		Updates database with the hash of the source code


- **obtain_source_digest**(self, _path):

	   Returns a hash of the file indicated by _path


- **find_source_file**(self, _path):

		Finds a source file for the file indacted by _path.

        _path may be to a .pyc/.so/.pyd or to a .py file.

        In the former case, the .py file is located and returned if available.
        Otherwise, simply returns the same _path that was supplied.
