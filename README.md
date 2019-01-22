[pythonjit](https://erose1337.github.io/pythonjit/)
==============

Automatically cross compiles .py files to .so (or .pyd) using Cython and import hooks.

How to use:

    import pythonjit
    pythonjit.enable()

And imports will automatically be cythonized.

For more performance benefits, use the decorators provided by cython to statically type variables and return types.
The relevant decorators are:

- `@cython.cfunc` (declares cdef function)
- `@cython.ccall` (declares cpdef function, callable from interpreted python)
- `@cython.returns` (declare return type)
- `@cython.declare` (declare variables and their types)
    - Can also use annotations in python 3 to declare cython types
- `@cython.locals` (declare multiple argument and local variable types for a function)
- `@cython.cclass` (declare cdef class)
- `@cython.inline` (equivalent to C inline keyword)
- `@cython.final` (makes subclassing impossible, enabling optimizations)

Types are also part of the cython module:

- `cython.int`
- `cython.longlong`
- `cython.struct`
- `cython.union`
- `cython.typedef`
- `cython.cast`
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
    - Alternatively, you can use the `compile_command` argument to specify a different compiler

# Notes/Known issues/Complications:

- `__file__` may not be available in compiled modules - see [here](https://stackoverflow.com/questions/19225188/what-method-can-i-use-instead-of-file-in-python#comment65304373_19225368) for a workaround

# Read the Docs

More documentation can be found on [readthedocs](https://pythonjit.readthedocs.io/en/latest/)
