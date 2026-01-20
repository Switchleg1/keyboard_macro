import json
import time
import yaml
import queue
import keyboard
import mouse

from keyboard._keyboard_event import KEY_DOWN, KEY_UP
from mouse._mouse_event import LEFT, RIGHT, MIDDLE, X, X2, UP, DOWN, DOUBLE

#globals
APP_VERSION             = "v0.3"
CONFIG_FILENAME         = "config.yaml"
DEFAULT_KEY_DELAY       = 0.05
DEFAULT_PLAY_SIZE       = 3
DEFAULT_RECORD_SIZE     = 1
DEFAULT_USE_KEYBOARD    = True
DEFAULT_USE_MOUSE       = True

use_keyboard            = DEFAULT_USE_KEYBOARD
use_mouse               = DEFAULT_USE_MOUSE

key_map                 = {}
mouse_map               = {}

macro_list              = []
key_delay               = DEFAULT_KEY_DELAY

record_queue_size       = DEFAULT_RECORD_SIZE
record_queue            = None

play_queue_size         = DEFAULT_PLAY_SIZE
play_queue              = None


def read_configuration(filename):
    global key_delay
    global record_queue_size
    global play_queue_size
    global use_keyboard
    global use_mouse

    try:
        #load config file
        print(f"Loading configuration file [{filename}]")

        with open(filename, 'r') as file:
            config_data = yaml.safe_load(file)

            #key_delay
            if 'key_delay' in config_data:
                key_delay = config_data['key_delay']
            print(f"  Set default key delay: {key_delay}")

            #play_queue_size
            if 'play_queue_size' in config_data:
                play_queue_size = config_data['play_queue_size']
            print(f"  Set play queue size: {play_queue_size}")

            #record_queue_size
            if 'record_queue_size' in config_data:
                record_queue_size = config_data['record_queue_size']
            print(f"  Set record queue size: {record_queue_size}")

            #use_keyboard
            if 'use_keyboard' in config_data:
                use_keyboard = config_data['use_keyboard']
            print(f"  Using keyboard input: {use_keyboard}")

            #use_mouse
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

                # build macro
                macro = {
                    'name'      : macro_dict['name'],
                    'filename'  : macro_dict['filename'],
                    'sequence'  : sequence,
                }

                if 'play_hotkey' in macro_dict:
                    macro['play_hotkey'] = macro_dict['play_hotkey'].split('+')
                    print(f"    assigning play_hotkey [{macro_dict['play_hotkey']}]")

                if 'record_hotkey' in macro_dict:
                    macro['record_hotkey'] = macro_dict['record_hotkey'].split('+')
                    print(f"    assigning record_key [{macro_dict['record_hotkey']}]")

                # add hot_key to the list
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
            json_events = [event.to_json() for event in macro['sequence']]
            # Use json.dump for a structured JSON file with a list of events
            json.dump(json_events, f, indent=4)

        print(f"Recording saved to {macro['filename']}")

    except Exception as e:
        print(f"Failed to save {macro['filename']} - {e}")


def load_sequence(filename):
    try:
        # Load the JSON strings from the file
        with open(filename, "r") as f:
            json_events = json.load(f)

        # Deserialize JSON strings back into KeyboardEvent objects
        current_playback_time = 0
        sequence = []
        for event_json in json_events:
            # Use json.loads to get a dictionary, then unpack to create KeyboardEvent
            event_dict = json.loads(event_json)
            event_dict["time"] = current_playback_time
            sequence.append(keyboard.KeyboardEvent(**event_dict))
            current_playback_time += key_delay

        return sequence

    except Exception as e:
        print(f"Failed to load {filename} - {e}")

        return None


def on_play_key(macro):
    try:
        play_queue.put_nowait(macro)

    except:
        print(f"Play queue is full - macro['name']")


def on_record_key(macro):
    try:
        record_queue.put_nowait(macro)

    except:
        print(f"Record queue is full - macro['name']")


def check_hot_key(hot_key_list):
    for key in hot_key_list:
        if key.startswith('mouse_'):
            key_sub = key[6:]
            if key_sub not in mouse_map or mouse_map[key_sub] == False:
                return False

        elif key not in key_map or key_map[key] == False:
            return False

    return True


def on_key_pressed(key):
    key_map[key] = True

    for macro in macro_list:
        if 'play_hotkey' in macro and check_hot_key(macro['play_hotkey']):
            on_play_key(macro)

        if 'record_hotkey' in macro and check_hot_key(macro['record_hotkey']):
            on_record_key(macro)


def on_key_released(key):
    key_map[key] = False


def on_key_event(event):
    if event.event_type == KEY_DOWN:
        on_key_pressed(event.name)

    elif event.event_type == KEY_UP:
        on_key_released(event.name)


def on_mouse_button(button, state):
    mouse_map[button] = state
    #print(f"{button} - {state}")


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
# Wait for record request
while True:
    if record_queue.qsize() > 0:
        macro = record_queue.get()

        print(f"***Record [{macro['name']}]***")
        print(f"Press 'Esc' to start recording.")
        keyboard.wait('esc')
        print(f"Press 'Esc' to stop.")

        # Record all key events until 'Esc' is pressed
        sequence = keyboard.record(until='esc')
        sequence.pop()
        sequence.pop(0)
        macro['sequence'] = sequence

        #set time to specified increments
        current_playback_time = 0
        for event in macro['sequence']:
            event.time = current_playback_time
            current_playback_time += key_delay

        #simplify the recording string
        sequence_string = ""
        for key in macro['sequence']:
            if key.event_type == 'down':
                sequence_string += f"{key.name} "

        print(f"Recorded: {sequence_string}")
        save_sequence(macro)
        play_queue.empty()

    elif play_queue.qsize() > 0:
        macro = play_queue.get()

        print(f"Playing - {macro['name']}") #[{macro['sequence']}]")
        keyboard.play(macro['sequence'], speed_factor=1.0)

    time.sleep(key_delay)