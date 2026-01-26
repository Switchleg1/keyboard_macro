import time
import queue
import keyboard
import mouse
import ctypes
import sys
import threading
import lib.Constants as Constants
import lib.ConfigFile as ConfigFile
import lib.Sequences as Sequences
import lib.Log as Log
import lib.Helpers as Helpers
from PyQt6.QtWidgets import QApplication
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
from mouse._mouse_event import MoveEvent, ButtonEvent, WheelEvent, LEFT, RIGHT, MIDDLE, X, X2, UP, DOWN, DOUBLE
from lib.UI.MainWindow import MainWindow
from lib.SettingType import SettingType

settings = {
    'start_minimized'                   : SettingType(Constants.DEFAULT_START_MINIMIZE, "Start minimized", 2),
    'key_timeout'                       : SettingType(Constants.DEFAULT_KEY_TIMEOUT, "Set key timeout", 2),

    'play_queue_size'                   : SettingType(Constants.DEFAULT_PLAY_SIZE, "Set play queue size", 2),
    'record_queue_size'                 : SettingType(Constants.DEFAULT_RECORD_SIZE, "Set record queue size", 2),

    'use_keyboard'                      : SettingType(Constants.DEFAULT_USE_KEYBOARD, "Using keyboard input", 2),
    'use_mouse'                         : SettingType(Constants.DEFAULT_USE_MOUSE, "Using mouse input", 2),
    'use_mouse_wheel'                   : SettingType(Constants.DEFAULT_USE_MOUSE_WHEEL, "Using mouse wheel input", 2),
    'use_gui'                           : SettingType(Constants.DEFAULT_USE_GUI, "Using GUI", 2),

    'default_playback_delay'            : SettingType(Constants.DEFAULT_PLAYBACK_DELAY, "Set playback delay", 2),
    'default_listen_during_playback'    : SettingType(Constants.DEFAULT_LISTEN_PLAYBACK, "Set listen for hotkey during playback", 2),
    'default_record_delay'              : SettingType(Constants.DEFAULT_RECORD_DELAY, "Set record delay values during record", 2),
    'default_record_mouse_movement'     : SettingType(Constants.DEFAULT_MOUSE_MOVEMENT, "Set record mouse movement during record", 2),
    'default_record_mouse_fps'          : SettingType(Constants.DEFAULT_MOUSE_FPS, "Set record mouse fps during record", 2),
    'default_playback_speed'            : SettingType(Constants.DEFAULT_PLAYBACK_SPEED, "Set playback speed scale", 2),
    'default_macro_cooldown'            : SettingType(Constants.DEFAULT_MACRO_COOLDOWN, "Set default macro cooldown", 2),
}

key_map                         = {}
mouse_map                       = {}
macro_list                      = []

record_macro                    = None
record_active                   = False
record_queue                    = None
record_last_time                = 0
record_last_movement            = 0
record_mouse_movement_delay     = 0

play_active                     = False
play_queue                      = None

macro_mutex                     = None
run_thread                      = True

main_window                     = None

#functions
def on_play_key(macro):
    try:
        if time.time() - macro['lastplay'] > macro['cooldown']:
            if play_active == False or macro['listen_during_playback']:
                macro['lastplay'] = time.time()
                play_queue.put_nowait(macro)

    except:
        Log.w(f"Play queue is full - {macro['name']}")


def on_record_key(macro):
    global record_macro
    global record_mouse_movement_delay
    global record_last_movement
    global record_last_time

    if record_macro is None:
        record_mouse_movement_delay = 1 / macro['record_mouse_fps'] if macro['record_mouse_movement'] else 0
        record_last_movement        = time.time() if macro['record_mouse_movement'] else 0
        record_last_time            = time.time() if macro['record_delay'] else 0
        record_macro                = macro


def check_hotkey_list(hotkey_list, isWheel=False, wheelDirection=UP):
    for hot_key in hotkey_list:
        isPressed = True if len(hot_key) > 0 else False
        for key in hot_key:
            if key.startswith('mouse_wheel_'):
                key_sub = key[12:]

                if isWheel == False or wheelDirection != key_sub:
                    isPressed = False

            elif key.startswith('mouse_'):
                key_sub = key[6:]
            
                if key_sub not in mouse_map or mouse_map[key_sub]['active'] == False or time.time() - mouse_map[key_sub]['time'] > settings['key_timeout'].value:
                    isPressed = False

            elif key not in key_map or key_map[key]['active'] == False or time.time() - key_map[key]['time'] > settings['key_timeout'].value:
                isPressed = False

        if isPressed == True:
            return True

    return False


def check_macros(isWheel=False, wheelDirection=UP):
    with macro_mutex:
        for macro in macro_list:
            if 'record_hotkey' in macro and check_hotkey_list(macro['record_hotkey'], isWheel, wheelDirection):
                on_record_key(macro)

            elif 'play_hotkey' in macro and check_hotkey_list(macro['play_hotkey'], isWheel, wheelDirection):
                on_play_key(macro)
        

def place_in_record_queue(name, state, time):
    global record_last_time

    key = {
        "name"  : name,
        "state" : state,
    }

    if record_last_time != 0:
        key['delay']  = time - record_last_time

        if key['delay'] < 0:
            key['delay'] = 0

        else:
            record_last_time = time

    try:
        record_queue.put_nowait(key)

    except:
        Log.w(f"Record queue is full - [{name}]")


def on_key_event(event):
    isPressed = event.event_type == KEY_DOWN

    key_map[event.name] = {
        'time'      : time.time(),
        'active'    : isPressed
    }

    if record_macro is not None:
        if record_active:
            place_in_record_queue(event.name, event.event_type, event.time)

    elif isPressed:
        check_macros()


def on_mouse_event(event):
    if isinstance(event, mouse.ButtonEvent):
        on_mouse_button(event)

    elif isinstance(event, mouse.MoveEvent):
        on_mouse_move(event)

    elif isinstance(event, mouse.WheelEvent):
        on_mouse_wheel(event)


def on_mouse_button(event):
    isPressed = event.event_type != UP

    mouse_map[event.button] = {
        'time'      : time.time(),
        'active'    : isPressed
    }

    if record_macro is not None:
        if record_active:
            place_in_record_queue(f"mouse_{event.button}", DOWN if isPressed else UP, event.time)

    elif isPressed:
        check_macros()


def on_mouse_wheel(event):
    if settings['use_mouse_wheel'].value == False:
        return

    button_state = UP if event.delta > 0 else DOWN

    if record_macro is not None:
        if record_active:
            place_in_record_queue(f"mouse_wheel_{button_state}", DOWN, event.time)

    else:
        check_macros(isWheel=True, wheelDirection=button_state)


def on_mouse_move(event):
    global record_last_movement

    if record_active == True and record_macro is not None and record_mouse_movement_delay > 0:
        if event.time - record_last_movement > record_mouse_movement_delay:
            place_in_record_queue(f"mouse_move", f"{event.x}:{event.y}", event.time)
            record_last_movement = event.time


def macro_thread_task():
    global settings
    global key_map
    global mouse_map
    global macro_list
    global record_macro
    global record_active
    global record_queue
    global record_last_time
    global record_last_movement
    global record_mouse_movement_delay
    global play_active
    global play_queue

    # The program continues to run, listening for the hotkey in a separate thread
    # Wait for item in either queue
    while run_thread:
        with macro_mutex:
            if record_macro is not None:
                Log.i(f"***Record [{record_macro['name']}]***")
                Log.i(f"Press 'Esc' to start recording.")

                #clear record queue
                if record_queue.qsize() > 0:
                    record_queue.get()

                #start accepting keys
                record_active = True

                #wait for esc
                key = record_queue.get()
                while key['name'] != 'esc' and key['state'] != DOWN:
                    key = record_queue.get()

                Log.i(f"Press 'Esc' to stop.")

                #record keys
                sequence = []
                key = record_queue.get()
                last_key = None
                while key['name'] != 'esc' or key['state'] == UP:
                    if (last_key is not None and key != last_key) or key['name'] == 'mouse_wheel':
                        sequence.append(key)

                    last_key = key
                    key = record_queue.get()

                #stop the recording and clear information
                record_active               = False
                record_mouse_movement_delay = 0
                record_last_movement        = 0
                record_last_time            = 0

                #simplify the recording string
                sequence_string = ""
                for key in sequence:
                    if key['state'] == 'down':
                        sequence_string += f"{key['name']} "

                Log.i(f"Recorded: {sequence_string}")

                record_macro['sequence'] = sequence

                Sequences.save_sequence(record_macro['filename'], record_macro['sequence'])
                record_macro['lastplay'] = time.time()
                record_macro = None

            elif play_queue.qsize() > 0:
                macro = play_queue.get()

                Log.i(f"Playing - {macro['name']}")
                play_active = True
                try:
                    for key in macro['sequence']:
                        #Find delay between keys
                        if macro['playback_speed'] > 0:
                            delay_time = (key['delay'] if 'delay' in key else macro['playback_delay']) / macro['playback_speed']

                        else:
                            delay_time = 0

                        #Find out if this is a move, wheel, button or key event
                        if key['name'] == ('mouse_move'):
                            if settings['use_mouse_wheel'].value:
                                mouse_position = key['state'].split(':')
                                mouse.move(mouse_position[0], mouse_position[1], True, delay_time)
                                delay_time = 0

                        elif key['name'].startswith('mouse_wheel_'):
                            if settings['use_mouse_wheel'].value:
                                key_sub = key['name'][12:]

                                if key_sub == DOWN:
                                    mouse.wheel(-1)

                                elif key_sub == UP:
                                    mouse.wheel(1)

                        elif key['name'].startswith('mouse_'):
                            if settings['use_mouse'].value:
                                key_sub = key['name'][6:]

                                if key['state'] == DOWN:
                                    mouse.press(key_sub)

                                else:
                                    mouse.release(key_sub)

                        elif settings['use_keyboard'].value:
                            keyboard.send(key['name'], key['state'] == DOWN, key['state'] == UP)

                        #Wait for the next key event
                        time.sleep(delay_time)

                except Exception as e:
                    Log.i(f"Failed - {e}")

                play_active = False

        time.sleep(settings['default_playback_delay'].value)


### Main ###
if __name__ == "__main__":
    Log.i(f"Starting keyboard_macro {Constants.APP_VERSION}")

    ConfigFile.read_configuration(Constants.CONFIG_FILENAME, settings, macro_list)

    record_queue = queue.Queue(maxsize = settings['record_queue_size'].value)
    play_queue = queue.Queue(maxsize = settings['play_queue_size'].value)
    macro_mutex = threading.Lock()

    if settings['use_keyboard'].value:
        keyboard.hook(lambda e: on_key_event(e))

    if settings['use_mouse'].value:
        mouse.hook(on_mouse_event)

    # Start the macro handling thread
    macro_thread = threading.Thread(target=macro_thread_task, args=())
    macro_thread.start()

    # Start application
    if settings['use_gui'].value:
        Helpers.minimize_console()

        app = QApplication(sys.argv)
        main_window = MainWindow(f"keyboard_macro {Constants.APP_VERSION}", settings, macro_list, macro_mutex)

        if settings['start_minimized'].value:
            main_window.showMinimized()

        app.exec()
        run_thread = False

    else:
        if settings['start_minimized'].value:
            Helpers.minimize_console()

        Log.set_output(print)
        Log.dump_buffer()

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        macro_thread.join()