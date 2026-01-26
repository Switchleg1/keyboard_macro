import time
from enum import Enum

class LogLevel(Enum):
    NONE        = 0
    ERROR       = 1
    WARN        = 2
    INFO        = 3
    DEBUG       = 4


output_function = None
log_level       = LogLevel.INFO
stored_values   = []


def set_output(func):
    global output_function

    output_function = func


def set_level(level):
    log_level = level


def dump_buffer():
    if output_function is not None:
         # Get the current time as a struct_time object
        named_tuple = time.localtime()

        # Format the time into a specific string format (Month/Day/Year, Hour:Minute:Second)
        time_string = time.strftime("%H:%M:%S", named_tuple)

        while len(stored_values) > 0:
            output_string = f"[{time_string}] {stored_values[0]}"
            output_function(output_string)

            del stored_values[0]



def d(out):
    _do_output(out, [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR])


def i(out):
    _do_output(out, [LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR])


def w(out):
    _do_output(out, [LogLevel.WARN, LogLevel.ERROR])


def e(out):
    _do_output(out, [LogLevel.ERROR])


def _do_output(out, level):
    if log_level in level:
        # Get the current time as a struct_time object
        named_tuple = time.localtime()

        # Format the time into a specific string format (Month/Day/Year, Hour:Minute:Second)
        time_string = time.strftime("%H:%M:%S", named_tuple)

        output_string = f"[{time_string}] {out}"
        if output_function is not None:
            output_function(output_string)

        else:
            stored_values.append(output_string)