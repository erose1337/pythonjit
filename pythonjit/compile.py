""" Command line program to compile modules. See python compile.py -h for usage. """

import argparse

import pythonjit

import cython

parser = argparse.ArgumentParser()
parser.add_argument("source_filename", help="The source file to be compiled")
parser.add_argument("-o", "--output_filename", help="The name of the compiled executable (without the .exe/.so/.pyd file extension")
parser.add_argument("-m", "--mode", help="Specifies a file extension (pyd, so, exe); Default is exe")
parser.add_argument("-v", "--verbosity", help="Increase output verbosity; Options are 0 (default) and 2", type=int)
parser.add_argument("-p", "--python_version", help="Sets the python version to 2 or 3 (default=2)", type=int)
parser.add_argument("-c", "--compile_command", help="Specifies the command used to execute the compiler; See `cross_compile` docs")

def main():
    """Command line program, `main` accepts no arguments. See `python compile.py -h for usage documentation"""
    args = parser.parse_args()
    source_files = list(item.strip() for item in args.source_filename.split(','))
    if args.output_filename:
        output_files = list(item.strip() for item in args.output_filename.split(','))
        if len(output_files) != len(source_files):
            raise ValueError("Non-matching quantity of input and output filenames")
    else:
        output_files = [None for item in source_files]

    mode = args.mode or "exe"
    version = args.python_version or '2'
    verbosity = args.verbosity or 0
    compile_command = args.compile_command or pythonjit._compile.COMPILE_COMMAND
    pythonjit.cross_compile(source_files, output_files, mode, version, verbosity, compile_command)
if not cython.compiled:
     main.__doc__ += '\n' + parser.format_help() #doesn't work when compiled

if __name__ == "__main__":
    main()
