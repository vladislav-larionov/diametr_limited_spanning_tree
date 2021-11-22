import time
from datetime import datetime


def timeit(func):
    """
    Decorator for measuring function's running time.
    """
    def measure_time(*args, **kw):
        start_time = time.time()
        print(f'start: {datetime.now()}')
        result = func(*args, **kw)
        print("Processing time of %s(): %.2f seconds." % (func.__qualname__, time.time() - start_time))
        return result
    return measure_time
