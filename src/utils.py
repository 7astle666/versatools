import sys
import os
import functools
import sys
from datetime import datetime

class Utils():
    """
    Utility functions
    """
    @staticmethod
    def ensure_directories_exist(directories):
        """
        Creates directories if they don't exist
        """
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

    @staticmethod
    def ensure_files_exist(files):
        """
        Creates files if they don't exist
        """
        for file in files:
            if not os.path.exists(file):
                with open(file, 'w'):
                    pass

    @staticmethod
    def clear_line(line: str) -> str:
        """
        Clears a line from spaces, tabs and newlines
        """
        return line.replace("\n", "").replace(" ", "").replace("\t", "")

    @staticmethod
    def return_res(response) -> str:
        """
        Returns a string with the response text and status code
        """
        return response.text + " HTTPStatus: " + str(response.status_code)

    @staticmethod
    def handle_exception(retries = 1, decorate_exception = True):
        """
        Decorator to retry executing a function x times until there's no exception
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                """
                Retry executing function x times until there's no exception
                """
                err = None
                err_line = None
                for _ in range(retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        err = str(e)
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        err_line = exc_tb.tb_next.tb_lineno
                else:
                    if decorate_exception:
                        err_msg = f"Error {err} on line {err_line}. Tried running {func.__name__}"

                        if retries == 1:
                            raise Exception(err_msg + " once")
                        else:
                            raise Exception(err_msg + f" {retries} times")
                    else:
                        raise Exception(err)
            return wrapper
        return decorator

    @staticmethod
    def utc_sec():
        """
        Returns the current UTC time in seconds
        """
        utc_time = datetime.utcnow()
        utc_seconds = round((utc_time - datetime(1970, 1, 1)).total_seconds())
        return utc_seconds


class Suppressor():
    """
    Context manager to suppress stdout (or any other stream)
    """
    def __enter__(self):
        # pylint: disable =attribute-defined-outside-init
        self.stdout = sys.stdout
        sys.stdout = self

    def __exit__(self, exception_type, value, traceback):
        sys.stdout = self.stdout
        if exception_type is not None:
            # Do normal exception handling
            raise Exception(f"Got exception: {exception_type} {value} {traceback}")

    def write(self, x):
        """
        Suppresses the output
        """

    def flush(self):
        """
        Suppresses the output
        """
