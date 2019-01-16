pythonjit
==============

Automatically cross compiles .py files to .so (or .pyd) using Cython and import hooks.

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

# Bugs in your code and compilation time

Cython is more stringent than the python interpreter when it comes to catching errors in code.
E.g. It will complain about NameErrors that occur in unreachable code, which the python interpreter will not do.
A larger/complex project may have issues to fix before Cython can compile it.

Cross compilation can take some time, especially for larger projects.
A caching mechanism is used to compensate for this, so the first run will be slower than future runs.

# Requirements

- `cython` must be installed
- `gcc` must be available (Windows users should install [MinGW](http://mingw.org) to gain access to `gcc`)

# Notes/Known issues/Complications:

- `__file__` may not be available in compiled modules - see[here](https://stackoverflow.com/questions/19225188/what-method-can-i-use-instead-of-file-in-python#comment65304373_19225368) for a workaround
- Supports python 2 and 3, but the default version is set to 2.

# Read the Docs

More documentation can be found on [readthedocs](https://pythonjit.readthedocs.io/en/latest/)


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


Multiple_Enable_Error
--------------

	No documentation available


Method resolution order:

	(<class 'pythonjit.Multiple_Enable_Error'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Not_Enabled_Error
--------------

	No documentation available


Method resolution order:

	(<class 'pythonjit.Not_Enabled_Error'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

cross_compile
--------------

**cross_compile**(file_list, output_names, mode, version, verbosity):

				No documentation available


disable
--------------

**disable**():

		 usage: disable() -> None

        Disables automatic compilation of imported python modules.
        Does not "uncompile" any previously compiled imported modules.
        enable can be called again to re-enable compilation of imported modules.

        Calling disable when compilation is not enabled will raise Not_Enabled_Error.


enable
--------------

**enable**(verbosity):

		 usage: enable(verbosity=0) -> None

        Enables automatic cross compilation of imported python modules via Cython.
        verbosity is an optional keyword argument that can be set to:

            - 0 for no output
            - 1 for the beginning of compilation of a module to be output
            - 2 for the progress of the compilation process to be output, plus the output from 1

        The Import_Hook created by calling enable() will live in the _STORAGE list in the pythonjit module.

        Calling enable when compilation is already enabled will raise Multiple_Enable_Error.
