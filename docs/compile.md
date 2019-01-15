# _compile.py
----

Handles the process of using cython and gcc to cross compile .py files into .pyx, then into .c, then into .so/.pyd/.exe.

While this module does expose one function that is intended to be available to end users, that function is aliased in the `pythonjit` module.

Users of pythonjit should not use this module, and instead should access the functionality through `pythonjit.cross_compile`.
