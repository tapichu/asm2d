from __future__ import print_function
import sys

# Error reporting

class ErrorReport:
    "A class to count errors and report totals."

    def __init__(self):
        self._num_errors = 0

    def has_errors(self):
        return self._num_errors > 0

    def num_errors(self):
        return self._num_errors

    def add_error(self):
        self._num_errors += 1

    def report_errors(self):
        if self.has_errors():
            if self.num_errors() == 1:
                print("There is 1 error.", file=sys.stderr)
            else:
                print("There are {0:d} errors.".format(self.num_errors()), file=sys.stderr)
            sys.exit(1)


def error(msg, *args, **kwargs):
    "Print an error message."
    if 'errors' in kwargs: kwargs['errors'].add_error()
    if 'lineno' in kwargs:
        print("ERROR: {0} (at line: {1:d})".format(msg.format(*args), kwargs['lineno']), file=sys.stderr)
    else:
        print("ERROR: {}".format(msg.format(*args)), file=sys.stderr)

def warn(msg, *args, **kwargs):
    "Print a warning message."
    if 'lineno' in kwargs:
        print("WARNING: {0} (at line: {1:d})".format(msg.format(*args), kwargs['lineno']), file=sys.stderr)
    else:
        print("WARNING: {}".format(msg.format(*args)), file=sys.stderr)
