import json
import lib.Log as Log


def save_sequence(filename, sequence):
    try:
        # Serialize events to a list of JSON strings and save to a file
        with open(filename, "w") as f:
            json.dump(sequence, f, indent=4)

        Log.i(f"Recording saved to {filename}")

    except Exception as e:
        Log.e(f"Failed to save {filename} - {e}")


def load_sequence(filename):
    try:
        # Load the JSON strings from the file
        with open(filename, "r") as f:
            return json.load(f)

    except Exception as e:
        Log.e(f"Failed to load {filename} - {e}")

        return None