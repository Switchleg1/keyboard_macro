import decimal
import ctypes
import sys

"""
Convert the given float to a string,
without resorting to scientific notation
"""
def float_to_str(f):
    # create a new context for this task
    ctx = decimal.Context()
    ctx.prec = 5

    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')

"""
Minimize the console window used by the python script in win32
"""
def minimize_console():
    if sys.platform == 'win32':
        # Get the handle for the current console window
        console_window = ctypes.windll.kernel32.GetConsoleWindow()
        if console_window:
            # 6 corresponds to the SW_MINIMIZE flag
            ctypes.windll.user32.ShowWindow(console_window, 6)