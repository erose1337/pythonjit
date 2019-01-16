pythonjit._compile
==============

 Handles the process of using cython and gcc to cross compile .py files into .pyx, then into .c, then into .so/.pyd/.exe.

While this module does expose one function that is intended to be available to end users, that function is aliased in the `pythonjit` module.

Users of pythonjit should not use this module, and instead should access the functionality through `pythonjit`.

ccompile
--------------

**ccompile**(file_list, output_names, mode, verbosity):

				No documentation available


convert_to_c
--------------

**convert_to_c**(file_names, mode, version, verbosity):

				No documentation available


convert_to_pyx
--------------

**convert_to_pyx**(file_list):

				No documentation available


cross_compile
--------------

**cross_compile**(file_list, output_names, mode, version, verbosity):

				No documentation available


pyx_to_compiled
--------------

**pyx_to_compiled**(file_list, output_names, mode, version, verbosity):

				No documentation available
