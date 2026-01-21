import json
import time
import yaml
import queue
import keyboard
import mouse

from keyboard._keyboard_event import KEY_DOWN, KEY_UP
from mouse._mouse_event import LEFT, RIGHT, MIDDLE, X, X2, UP, DOWN, DOUBLE

#globals
APP_VERSION                     = "v0.65"
CONFIG_FILENAME                 = "config.yaml"
DEFAULT_KEY_DELAY               = 0.05
DEFAULT_PLAY_SIZE               = 1
DEFAULT_RECORD_SIZE             = 1
DEFAULT_USE_KEYBOARD            = True
DEFAULT_USE_MOUSE               = True
DEFAULT_KEY_TIMEOUT             = 30.0
DEFAULT_MACRO_COOLDOWN          = 1.0
DEFAULT_LISTEN_PLAYBACK         = True

key_delay                       = DEFAULT_KEY_DELAY
key_timeout                     = DEFAULT_KEY_TIMEOUT

use_keyboard                    = DEFAULT_USE_KEYBOARD
use_mouse                       = DEFAULT_USE_MOUSE

key_map                         = {}
mouse_map                       = {}

default_listen_during_playback  = DEFAULT_LISTEN_PLAYBACK

macro_default_cooldown          = DEFAULT_MACRO_COOLDOWN
macro_list                      = []

record_macro                    = None
record_active                   = False
record_queue_size               = DEFAULT_RECORD_SIZE
record_queue                    = None

play_active                     = False
play_queue_size                 = DEFAULT_PLAY_SIZE
play_queue                      = None


def read_configuration(filename):
    global key_delay
    global key_timeout
    global default_listen_during_playback
    global record_queue_size
    global play_queue_size
    global use_keyboard
    global use_mouse
    global macro_default_cooldown

    try:
        #load config file
        print(f"Loading configuration file [{filename}]")

        with open(filename, 'r') as file:
            config_data = yaml.safe_load(file)

            #global settings
            if 'key_delay' in config_data:
                key_delay = config_data['key_delay']
            print(f"  Set default key delay: {key_delay}")
            
            if 'key_timeout' in config_data:
                key_timeout = config_data['key_timeout']
            print(f"  Set key timeout: {key_timeout}")

            if 'default_listen_during_playback' in config_data:
                default_listen_during_playback = config_data['default_listen_during_playback']
            print(f"  Set listen for hotkey during playback: {default_listen_during_playback}")

            if 'macro_default_cooldown' in config_data:
                macro_default_cooldown = config_data['macro_default_cooldown']
            print(f"  Set default macro cooldown: {macro_default_cooldown}")

            if 'play_queue_size' in config_data:
                play_queue_size = config_data['play_queue_size']
            print(f"  Set play queue size: {play_queue_size}")

            if 'record_queue_size' in config_data:
                record_queue_size = config_data['record_queue_size']
            print(f"  Set record queue size: {record_queue_size}")

            if 'use_keyboard' in config_data:
                use_keyboard = config_data['use_keyboard']
            print(f"  Using keyboard input: {use_keyboard}")

            if 'use_mouse' in config_data:
                use_mouse = config_data['use_mouse']
            print(f"  Using mouse input: {use_mouse}")


            macro_positon = 0
            macro_string = f"macro_{macro_positon}"
            while macro_string in config_data:
                macro_dict = config_data[macro_string]

                if 'name' not in macro_dict:
                    print(f"  {macro_string} - does not have a name")
                    break

                if 'play_hotkey' not in macro_dict and 'record_key' not in macro_dict:
                    print(f"  {macro_dict['name']} - must have [play_hotkey] or [record_hotkey]")
                    break

                if 'filename' not in macro_dict:
                    print(f"  {macro_dict['name']} - does not have a filename")
                    break

                print(f"  Loading [{macro_dict['name']}] - [{macro_dict['filename']}]")
                sequence = load_sequence(macro_dict['filename'])
                if sequence is None:
                    break

                cooldown = macro_default_cooldown
                if 'cooldown' in macro_dict:
                    cooldown = macro_dict['cooldown']
                    print(f"    setting cooldown {macro_dict['cooldown']}")

                listen_during_playback = default_listen_during_playback
                if 'listen_during_playback' in macro_dict:
                    listen_during_playback = macro_dict['listen_during_playback']
                    print(f"    setting listen during playback {macro_dict['listen_during_playback']}")

                # build macro
                macro = {
                    'name'                      : macro_dict['name'],
                    'filename'                  : macro_dict['filename'],
                    'sequence'                  : sequence,
                    'lastplay'                  : time.time(),
                    'cooldown'                  : cooldown,
                    'listen_during_playback'    : listen_during_playback
                }

                if 'play_hotkey' in macro_dict:
                    macro['play_hotkey'] = macro_dict['play_hotkey'].split('+')
                    print(f"    assigning play_hotkey [{macro_dict['play_hotkey']}]")

                if 'record_hotkey' in macro_dict:
                    macro['record_hotkey'] = macro_dict['record_hotkey'].split('+')
                    print(f"    assigning record_key [{macro_dict['record_hotkey']}]")

                # add macro to the list
                macro_list.append(macro)

                macro_positon += 1
                macro_string = f"macro_{macro_positon}"

        print(f"Finished reading configuration file [{filename}]")

    except Exception as e:
        print(f"Failed to load configuration file [{filename}] - {e}")


def save_sequence(macro):
    try:
        # Serialize events to a list of JSON strings and save to a file
        with open(macro['filename'], "w") as f:
            json.dump(macro['sequence'], f, indent=4)

        print(f"Recording saved to {macro['filename']}")

    except Exception as e:
        print(f"Failed to save {macro['filename']} - {e}")


def load_sequence(filename):
    try:
        # Load the JSON strings from the file
        with open(filename, "r") as f:
            return json.load(f)

    except Exception as e:
        print(f"Failed to load {filename} - {e}")

        return None


def on_play_key(macro):
    try:
        if time.time() - macro['lastplay'] > macro['cooldown']:
            if play_active == False or macro['listen_during_playback']:
                macro['lastplay'] = time.time()
                play_queue.put_nowait(macro)

    except:
        print(f"Play queue is full - {macro['name']}")


def on_record_key(macro):
    global record_macro

    if record_macro is None:
        record_macro = macro


def check_hotkey(hot_key_list):
    for key in hot_key_list:
        if key.startswith('mouse_'):
            key_sub = key[6:]
            if key_sub not in mouse_map or mouse_map[key_sub]['active'] == False or time.time() - mouse_map[key_sub]['time'] > key_timeout:
                return False

        elif key not in key_map or key_map[key]['active'] == False or time.time() - key_map[key]['time'] > key_timeout:
            return False

    return True


def check_macros():
    for macro in macro_list:
        if 'record_hotkey' in macro and check_hotkey(macro['record_hotkey']):
            on_record_key(macro)

        elif 'play_hotkey' in macro and check_hotkey(macro['play_hotkey']):
            on_play_key(macro)
        

def place_key_in_record_queue(name, state):
    key = {
        "name"  : name,
        "state" : state
    }

    try:
        record_queue.put_nowait(key)

    except:
        print(f"Record queue is full - [{name}]")


def on_key_event(event):
    isPressed = event.event_type == KEY_DOWN

    key_map[event.name] = {
        'time'      : time.time(),
        'active'    : isPressed
    }

    if record_macro is not None:
        if record_active:
            place_key_in_record_queue(event.name, event.event_type)

    elif isPressed:
        check_macros()


def on_mouse_button(button, state):
    isPressed = state == DOWN

    mouse_map[button] = {
        'time'      : time.time(),
        'active'    : isPressed
    }

    if record_macro is not None:
        if record_active:
            place_key_in_record_queue(f"mouse_{button}", state)

    elif isPressed:
        check_macros()


### Begin ###

print(f"Starting keyboard_macro {APP_VERSION}")

read_configuration(CONFIG_FILENAME)

record_queue = queue.Queue(maxsize = record_queue_size)
play_queue = queue.Queue(maxsize = play_queue_size)

if use_keyboard:
    keyboard.hook(lambda e: on_key_event(e))

if use_mouse:
    mouse.on_button(on_mouse_button, (LEFT, DOWN), [LEFT], [DOWN])
    mouse.on_button(on_mouse_button, (LEFT, UP), [LEFT], [UP])
    mouse.on_button(on_mouse_button, (RIGHT, DOWN), [RIGHT], [DOWN])
    mouse.on_button(on_mouse_button, (RIGHT, UP), [RIGHT], [UP])
    mouse.on_button(on_mouse_button, (MIDDLE, DOWN), [MIDDLE], [DOWN])
    mouse.on_button(on_mouse_button, (MIDDLE, UP), [MIDDLE], [UP])
    mouse.on_button(on_mouse_button, (X, DOWN), [X], [DOWN])
    mouse.on_button(on_mouse_button, (X, UP), [X], [UP])
    mouse.on_button(on_mouse_button, (X2, DOWN), [X2], [DOWN])
    mouse.on_button(on_mouse_button, (X2, UP), [X2], [UP])

# The program continues to run, listening for the hotkey in a separate thread
# Wait for item in either queue
while True:
    if record_macro is not None:
        print(f"***Record [{record_macro['name']}]***")
        print(f"Press 'Esc' to start recording.")

        #clear record queue
        if record_queue.qsize() > 0:
            record_queue.get()

        #start accepting keys
        record_active = True

        #wait for esc
        key = record_queue.get()
        while key['name'] != 'esc' and key['state'] != DOWN:
            key = record_queue.get()

        print(f"Press 'Esc' to stop.")

        #record keys
        sequence = []
        key = record_queue.get()
        last_key = None
        while key['name'] != 'esc' or key['state'] == UP:
            if last_key is not None and key != last_key:
                sequence.append(key)

            last_key = key
            key = record_queue.get()

        record_active = False
        record_macro['sequence'] = sequence

        #simplify the recording string
        sequence_string = ""
        for key in sequence:
            if key['state'] == 'down':
                sequence_string += f"{key['name']} "

        print(f"Recorded: {sequence_string}")

        save_sequence(record_macro)
        record_macro['lastplay'] = time.time() + record_macro['cooldown']
        record_macro = None

    elif play_queue.qsize() > 0:
        macro = play_queue.get()

        print(f"Playing - {macro['name']}")
        play_active = True
        for key in macro['sequence']:
            if key['name'].startswith('mouse_'):
                key_sub = key['name'][6:]
                if key['state'] == DOWN:
                    mouse.press(key_sub)

                else:
                    mouse.release(key_sub)

            else:
                keyboard.send(key['name'], key['state'] == 'down', key['state'] == 'up')

            time.sleep(key_delay)

        play_active = False

    time.sleep(key_delay)