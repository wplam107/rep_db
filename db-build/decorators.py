import functools

# Wrapper for error logging
def error_logging(func):
    @functools.wraps(func)
    def wrapper_error(*args):
        data = None
        error = None
        try:
            data = func(*args)
        except Exception as e:
            error = e
        return data, error
    return wrapper_error