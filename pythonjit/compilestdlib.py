""" Compiles python standard library modules ahead of time. """
import argparse # cannot compile anyways because it uses "const" as a variable name

import pythonjit

parser = argparse.ArgumentParser()
parser.add_argument("python_dir", help="The location of the python standard library files")
parser.add_argument("-v", "--verbosity", help="The verbosity level to pass to pythonjit.enable")
parser.add_argument("-db", "--database", help="The database file to use")
parser.add_argument("-cd", "--code_dir", help="The directory to place the compiled files")

DONT_COMPILE = ("antigravity", "this",# importing causes them to run, no benefit to compiling them anyways
                "test.regrtest",      # test.regrtest causes RuntimeError for some reason (apparently not supposed to import it anyways)
                "lib2to3.pgen.conv",  # causes ImportError: no module named pgen2
                "lib2to3.pgen2.conv", # ImportError
                "glib.__init__",      # NameError (references/imports a compiled module with a different name)
                "apt.auth",           # gcc chokes on the cross compiled variant
                "gobject.__init__",   # NameError
                "keyring.backends._OS_X_API", # OSError (probably won't happen if actually running OSX)
                "keyring.tests.test_backend", # ImportError: No module named pytest
                "wstools.XMLSchema",  # has an actual bug in it; Cython finds an undefined variable at line 2971
                "keyring.devpi_client", # ImportError: no module named pluggy
                "wstools.tests.test_t1",# main not defined (probably some metaprogramming hack going on)
                "setuptools",         # uses "include" as a variable name
                "Cython.Compiler.Main", # uses "include" as a variable name
                "Cython.Utils",       # uses "include" as a variable name
                "Cython.Compiler.PyrexTypes", # uses "signed" as a variable name
                "Cython.Compiler.Code", # uses "include" as a variable name
                "Cython.Compiler.TypeSlots",  # undeclared name not builtin
                "pygtkcompat",     # ImportError
                "gtk.dsextras",       # ImportError
                "gtk.compat",         # TypeError (it tries to __init__ a module without a name argument)
                "PyQt4.uic.uiparser", # uses "include" as a variable name
                "PyQt4.uic.pyuic",    # runs code not wrapped in if __name__ == "__main__":; it uses a parser and complains about this programs options
                "defusedxml.lxml",    # ImportError
                "setuptools.lib2to3_ex", # ImportError
                "SOAPpy.Errors",      # undeclared name not builtin
                "SOAPpy.NS",          # undeclared name
                "SOAPpy.Parser",      # Empty declarator (unclosed paranthesis?)
                "SOAPpy.Types",       # calls repr with wrong number of arguments,
                "SOAPpy.GSIServer",   # ImportError
                "encodings.mbcs",     # ImportError
                "distutils.msvc9compiler", # ImportError (may work if running Windows)
                "distutils.command.bdist_msi",  # ImportError
                "distutils.command.install_egg_info",   # NameError
                "xml.etree.ElementInclude", # uses "include" as a variable name
                "test.support.__init__") # must be imported from test package

IGNORE_PACKAGES = ("gtk-2.0", "gtk-2.0.gio", "PyQt4.uic.widget-plugins",
                   "lib2to3", "lib-tk", "plat-x86_64-linux-gnu")

def compile_stdlib(python_dir="/usr/lib/python2.7/",
                   dont_compile=DONT_COMPILE,
                   ignore_packages=IGNORE_PACKAGES,
                   **kwargs):
    """ usage: compile_stdlib(python_dir="/usr/lib/python2.7/",
                              dont_compile=compilestdlib.DONT_COMPILE,
                              ignore_packages=compilestdlib.IGNORE_PACKAGES
                              **kwargs) => None

        Compiles all python files in python_dir (recursively)
        python_dir is a string indicating a directory
        dont_compile is an iterable of fully-qualified (package.module.module) module names that should be not be compiled
        ignore_packages is an iterable of package names that should not have any of their modules compiled
        kwargs are passed to `pythonjit.enable` (see pythonjit.enable for available options)"""
    print("Compiling all python standard library modules (this will take a while...)")
    kwargs.setdefault("ignore_compilation_failure", True) # modules in the standard library that don't compile can't really be helped (yet)
    pythonjit.enable(**kwargs)
    import importlib # importing here so they get compiled
    import os
    import traceback
    import sys
    _root_dir_length = len(python_dir.split(os.path.sep))
    for dirname, path, filenames in os.walk(python_dir):
        package = dirname.split(os.path.sep)[_root_dir_length:]
        if package and package[0] == "dist-packages":
            del package[0]
        package = '.'.join(package)
        if package in ignore_packages:
            continue
        if package == "gtk-2.0.gtk":
            package = "gtk"

        print('-' * 80)
        if package:
            print("Compiling package: {}".format(package))
        else:
            print("Compiling entries in {}".format(dirname))
    #    raw_input()
        for filename in filenames:
            module_name, extension = os.path.splitext(filename)
            #if module_name == "__main__":
            #    module_name = "main"
            if package:
                module_name = '.'.join((package, module_name))

            if extension == ".py" and module_name not in dont_compile:
                print("Compiling: {}".format(module_name))
                try:
                    importlib.import_module(module_name)
                except ImportError:
                    if "__main__" in module_name:
                        module_name = module_name.replace("__main__", "main")
                        print("Trying again; Compiling {} instead".format(module_name))
                        importlib.import_module(module_name)
                    elif kwargs["verbosity"]:
                        print(traceback.format_exc())
                except ValueError:
                    if module_name == "ctypes.wintypes" and "win" not in sys.platform:
                        continue
                    else:
                        raise
    pythonjit.disable()

if __name__ == "__main__":
    args = parser.parse_args()
    kwargs = dict()
    if args.verbosity:
        kwargs["verbosity"] = args.verbosity
    else:
        kwargs["verbosity"] = 0
    if args.database:
        kwargs["db_name"] = args.database
    if args.code_dir:
        kwargs["code_dir"] = args.code_dir
    compile_stdlib(args.python_dir, **kwargs)
