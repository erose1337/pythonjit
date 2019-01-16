pythonjit._cythonhook
==============

 Provides a [module finder](https://www.python.org/dev/peps/pep-0302/) class.

This is not a public facing module; Users of pythonjit should use `pythonjit.enable` to automatically compile imported modules, or `pythonjit.cross_compile` as a utility to compile modules without importing them in python (e.g. in order to distribute them).

The `Import_Hook` class inserts itself into `sys.meta_path` when instantiated. When `import` statements are used, `Import_Hook` has the opportunity to locate the file to be imported. It uses this opportunity to locate the .py source code file for the module (if available), and uses `_compile.cross_compile` it to a static library.

After that, it's job is done; It passes the responsibility to find and load modules to the next or default finder/loader. That finder/loader will find the compiled version of the imported module, which will be used instead of the source code version of the module.

Import_Hook
--------------

	 This object is automatically instantiated and inserted into
        sys.meta_path as the first entry when instantiated. 


Method resolution order: 

	(<class 'pythonjit._cythonhook.Import_Hook'>, <type 'object'>)

- **find_module**(self, module_name, path):

				No documentation available


- **cross_compile**(self, _path):

				No documentation available


- **update_db**(self, module_name, source_digest, old_digest):

				No documentation available


- **obtain_source_digest**(self, _path):

				No documentation available


- **find_source_file**(self, _path):

				No documentation available
