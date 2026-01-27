import time
from enum import Enum


class LogLevel(Enum):
    NONE        = 0
    ERROR       = 1
    WARN        = 2
    INFO        = 3
    DEBUG       = 4


#globals
output_function     = None
log_level           = LogLevel.INFO
stored_log_entries  = []


"""
Used to set output function (print or log function)
"""
def set_output(func):
    global output_function

    output_function = func

"""
Set logging level
"""
def set_level(level):
    global log_level

    log_level = level

"""
Flush all data stored in the buffer to output function
"""
def dump_buffer(max_count=99999):
    if output_function is not None:
         # Get the current time as a struct_time object
        named_tuple = time.localtime()

        # Format the time into a specific string format (Month/Day/Year, Hour:Minute:Second)
        time_string = time.strftime("%H:%M:%S", named_tuple)

        #push line by line each stored in the buffer to output function
        while len(stored_log_entries) > 0 and max_count > 0:
            output_function(stored_log_entries[0])

            del stored_log_entries[0]
            max_count -= 1


"""
Remove and return a chunk of items stored in the buffer
"""
def receive_buffer(max_count=99999):
    global stored_log_entries

    if len(stored_log_entries) == 0:
        return []

    buffer_len = max_count if max_count < len(stored_log_entries) else len(stored_log_entries)
    
    ret_buffer = stored_log_entries[:buffer_len]
    stored_log_entries = stored_log_entries[buffer_len:]

    return ret_buffer


"""
Debug level log
"""
def d(out):
    _put_to_output(out, [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR])


"""
Info level log
"""
def i(out):
    _put_to_output(out, [LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR])


"""
Warning level log
"""
def w(out):
    _put_to_output(out, [LogLevel.WARN, LogLevel.ERROR])


"""
Error level log
"""
def e(out):
    _put_to_output(out, [LogLevel.ERROR])


"""
Main log evaluation function
"""
def _put_to_output(out, level):
    if log_level in level:
        # Get the current time as a struct_time object
        named_tuple = time.localtime()

        # Format the time into a specific string format (Hour:Minute:Second)
        time_string = time.strftime("%H:%M:%S", named_tuple)

        #build log string and either push to output if function is set else store it in the buffer
        output_string = f"[{time_string}] {out}"
        if output_function is not None:
            output_function(output_string)

        else:
            stored_log_entries.append(output_string)