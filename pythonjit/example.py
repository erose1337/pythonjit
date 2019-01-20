import timeit

import cython

@cython.cfunc
@cython.returns(cython.ulonglong)
@cython.locals(x=cython.ulonglong, i=cython.ulong)
def mathy_function(x):
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
    print("Executing interpreted version of function...")
    start = timeit.default_timer()
    output1 = mathy_function_python_version(8)
    end = timeit.default_timer()
    print("Time taken: {}".format(end - start))

    print("Executing compiled version of function...")
    start = timeit.default_timer()
    output2 = mathy_function(8)
    end = timeit.default_timer()
    print("Time taken: {}".format(end - start))

    assert output1 == output2, (output1, output2)

if __name__ == "__main__":
    test_function()
