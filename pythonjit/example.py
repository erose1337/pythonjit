import timeit

import cython

@cython.cfunc
@cython.returns(cython.ulonglong)
@cython.locals(x=cython.ulonglong, i=cython.ulong)
def mathy_function_cfunc(x):
    for i in range(1000000):
        x += x + 1
        x *= x
        #x &= 0xFFFFFFFFFFFFFFFF not necessary to perform this step
    return x

@cython.ccall
@cython.returns(cython.ulonglong)
@cython.locals(x=cython.ulonglong, i=cython.ulong)
def mathy_function_ccall(x):
    for i in range(1000000):
        x += x + 1
        x *= x
        #x &= 0xFFFFFFFFFFFFFFFF not necessary to perform this step
    return x

def mathy_function_python_version(x):
    for i in range(1000000):
        x += x + 1
        x *= x
        x &= 0xFFFFFFFFFFFFFFFF
    return x

def test_function():
    if not cython.compiled:
        import pythonjit
        raise pythonjit.Not_Compiled_Error("must run compiled version to receive performance benefits")
    print("Executing python version of function...")
    start = timeit.default_timer()
    output1 = mathy_function_python_version(8)
    end = timeit.default_timer()
    print("Time taken: {}".format(end - start))

    print("Executing cfunc version of function...")
    start = timeit.default_timer()
    output2 = mathy_function_cfunc(8)
    end = timeit.default_timer()
    print("Time taken: {}".format(end - start))

    assert output1 == output2, (output1, output2)

    print("Executing ccall version of function...")
    start = timeit.default_timer()
    output3 = mathy_function_ccall(8)
    end = timeit.default_timer()
    print("Time taken: {}".format(end - start))

    assert output3 == output2 == output1

if __name__ == "__main__":
    test_function()
