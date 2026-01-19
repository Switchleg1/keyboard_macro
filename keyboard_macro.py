import json
import time
import yaml
import keyboard

from keyboard._keyboard_event import KEY_DOWN, KEY_UP

#globals
APP_VERSION         = "v0.2"
CONFIG_FILENAME     = "config.yaml"
DEFAULT_KEY_DELAY   = 0.05

key_map             = {}
hot_keys            = []
sequences           = []
key_delay           = DEFAULT_KEY_DELAY

record_hot_key      = None
record_start        = False


def read_configuration(filename):
    try:
        #load config file
        print(f"Loading configuration file [{filename}]")

        with open(filename, 'r') as file:
            config_data = yaml.safe_load(file)

            if 'key_delay' in config_data:
                key_delay = config_data['key_delay']

            print(f"  Set default key delay: {key_delay}")

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

                # build hotkey
                hot_key = {
                    'name'      : macro_dict['name'],
                    'filename'  : macro_dict['filename'],
                    'sequence'  : sequence,
                }

                if 'play_hotkey' in macro_dict:
                    hot_key['play_hotkey'] = macro_dict['play_hotkey'].split('+')
                    print(f"    assigning play_hotkey [{macro_dict['play_hotkey']}]")

                if 'record_hotkey' in macro_dict:
                    hot_key['record_hotkey'] = macro_dict['record_hotkey'].split('+')
                    print(f"    assigning record_key [{macro_dict['record_hotkey']}]")

                # add hot_key to the list
                hot_keys.append(hot_key)

                macro_positon += 1
                macro_string = f"macro_{macro_positon}"

        print(f"Finished reading configuration file [{filename}]")

    except Exception as e:
        print(f"Failed to load configuration file [{filename}] - {e}")


def save_sequence(hot_key):
    try:
        # Serialize events to a list of JSON strings and save to a file
        with open(hot_key['filename'], "w") as f:
            json_events = [event.to_json() for event in hot_key['sequence']]
            # Use json.dump for a structured JSON file with a list of events
            json.dump(json_events, f, indent=4)

        print(f"Recording saved to {hot_key['filename']}")

    except Exception as e:
        print(f"Failed to save {hot_key['filename']} - {e}")


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


def on_play_key(hot_key):
    print(f"Playing - {hot_key['name']}") #[{hot_key['sequence']}]")
    keyboard.play(hot_key['sequence'], speed_factor=1.0)


def on_record_key(hot_key):
    global record_hot_key
    global record_start

    if record_start == False:
        record_hot_key = hot_key
        record_start = True


def check_hot_key(hot_key_string):
    for c in hot_key_string: 
        if c not in key_map or key_map[c] == False:
            return False

    return True


def on_key_pressed(key):
    key_map[key] = True

    for hot_key in hot_keys:
        if 'play_hotkey' in hot_key and check_hot_key(hot_key['play_hotkey']):
            on_play_key(hot_key)

        if 'record_hotkey' in hot_key and check_hot_key(hot_key['record_hotkey']):
            on_record_key(hot_key)


def on_key_released(key):
    key_map[key] = False


def on_key_event(event):
    if event.event_type == KEY_DOWN:
        on_key_pressed(event.name)

    elif event.event_type == KEY_UP:
        on_key_released(event.name)


### Begin ###

print(f"Starting keyboard_macro {APP_VERSION}")
read_configuration(CONFIG_FILENAME)
keyboard.hook(lambda e: on_key_event(e))

# The program continues to run, listening for the hotkey in a separate thread
# Wait for record request
while True:
    if record_start == True:
        print(f"***Record [{record_hot_key['name']}]***")
        print(f"Press 'Esc' to start recording.")
        keyboard.wait('esc')
        print(f"Press 'Esc' to stop.")

        # Record all key events until 'Esc' is pressed
        record_hot_key['sequence'] = keyboard.record(until='esc')
        record_hot_key['sequence'].pop()
        record_hot_key['sequence'].pop(0)

        #set time to specified increments
        current_playback_time = 0
        for event in record_hot_key['sequence']:
            event.time = current_playback_time
            current_playback_time += key_delay

        print(f"Recorded: {record_hot_key['sequence']}")
        save_sequence(record_hot_key)
        record_start = False

    time.sleep(1)