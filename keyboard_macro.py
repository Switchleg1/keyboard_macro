import keyboard
import json
import time
import yaml

#globals
CONFIG_FILENAME     = "config.yaml"
DEFAULT_KEY_DELAY   = 0.05

sequences = []
key_delay = DEFAULT_KEY_DELAY

record_name = ""
record_filename = ""
record_position = 0
record_start = False


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
                if sequence is not None:
                    sequences.append(sequence)

                else:
                    break

                if 'play_hotkey' in macro_dict:
                    print(f"    assigning play_hotkey [{macro_dict['play_hotkey']}]")
                    keyboard.add_hotkey(macro_dict['play_hotkey'], on_hotkey_play_trigger, args=[macro_positon, macro_dict['name']])

                if 'record_hotkey' in macro_dict:
                    print(f"    assigning record_key [{macro_dict['record_hotkey']}]")
                    keyboard.add_hotkey(macro_dict['record_hotkey'], on_hotkey_record_trigger, args=[macro_positon, macro_dict['name'], macro_dict['filename']])

                macro_positon += 1
                macro_string = f"macro_{macro_positon}"

        print(f"Finished reading configuration file [{filename}]")

    except Exception as e:
        print(f"Failed to load configuration file [{filename}] - {e}")


def save_sequence(sequence_position, filename):
    try:
        # Serialize events to a list of JSON strings and save to a file
        with open(filename, "w") as f:
            json_events = [event.to_json() for event in sequences[sequence_position]]
            # Use json.dump for a structured JSON file with a list of events
            json.dump(json_events, f, indent=4)

        print(f"Recording saved to {filename}")

    except Exception as e:
        print(f"Failed to save {filename} - {e}")


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


def on_hotkey_play_trigger(sequence_position, sequence_name):
    print(f"Playing - {sequence_name}") #[{sequences[sequence_position]}]")
    keyboard.play(sequences[sequence_position], speed_factor=1.0)


def on_hotkey_record_trigger(sequence_position, sequence_name, sequence_filename):
    global record_name
    global record_filename
    global record_start
    global record_position

    if record_start == False:
        record_name = sequence_name
        record_filename = sequence_filename
        record_position = sequence_position
        record_start = True


### Begin ###

read_configuration(CONFIG_FILENAME)

# The program continues to run, listening for the hotkey in a separate thread
# Wait for record request
while True:
    if record_start == True:
        print(f"***Record [{record_name}]***")
        print(f"Press 'Esc' to start recording.")
        keyboard.wait('esc')
        print(f"Press 'Esc' to stop.")

        # Record all key events until 'Esc' is pressed
        sequences[record_position] = keyboard.record(until='esc')
        sequences[record_position].pop()
        sequences[record_position].pop(0)

        #set time to specified increments
        current_playback_time = 0
        for event in sequences[record_position]:
            event.time = current_playback_time
            current_playback_time += key_delay

        print(f"Recorded: {sequences[record_position]}")
        save_sequence(record_position, record_filename)
        record_start = False

    time.sleep(1)