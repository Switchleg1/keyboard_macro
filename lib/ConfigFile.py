import time
import yaml
import lib.Sequences as Sequences
import lib.HotKeys as HotKeys
from lib.SettingType import SettingType

macro_options = {
    'listen_during_playback'    : SettingType('default_listen_during_playback', 'setting listen during playback', indent=4),
    'playback_delay'            : SettingType('default_playback_delay', 'setting playback delay to', indent=4),
    'record_delay'              : SettingType('default_record_delay', 'setting record delay to', indent=4),
    'record_mouse_movement'     : SettingType('default_record_mouse_movement', 'setting record mouse movement to', indent=4),
    'record_mouse_fps'          : SettingType('default_record_mouse_fps', 'setting record mouse fps to', indent=4),
    'playback_speed'            : SettingType('default_playback_speed', 'setting playback speed to', indent=4),
    'cooldown'                  : SettingType('default_macro_cooldown', 'setting cooldown to', indent=4),
}


#functions
def read_configuration(filename, settings, macro_list):

    try:
        #load config file
        print(f"Loading configuration file [{filename}]")

        with open(filename, 'r') as file:
            config_data = yaml.safe_load(file)

            #global settings
            for setting in settings:
                if setting in config_data:
                    settings[setting].value = config_data[setting]

                settings[setting].print()


            #clear and load macros
            while len(macro_list):
                del macro_list[0]

            macro_positon = 0
            macro_string = f"macro_{macro_positon}"
            while macro_string in config_data:
                macro_dict = config_data[macro_string]

                #check for required items
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
                sequence = Sequences.load_sequence(macro_dict['filename'])

                # build macro
                macro = {
                    'name'                      : macro_dict['name'],
                    'filename'                  : macro_dict['filename'],
                    'sequence'                  : sequence,
                    'lastplay'                  : time.time(),
                }

                #add hotkey lists
                if 'play_hotkey' in macro_dict:
                    macro['play_hotkey'] = HotKeys.string_to_list(macro_dict['play_hotkey'])
                    print(f"    assigning play_hotkey [{macro_dict['play_hotkey']}]")

                if 'record_hotkey' in macro_dict:
                    macro['record_hotkey'] = HotKeys.string_to_list(macro_dict['record_hotkey'])
                    print(f"    assigning record_key [{macro_dict['record_hotkey']}]")

                #add optional items
                for option_key, option_value in macro_options.items():
                    macro_value = settings[option_value.value].value
                    if option_key in macro_dict:
                        macro_value = macro_dict[option_key]

                        option_value.print_value(macro_value)

                    macro[option_key] = macro_value


                # add macro to the list
                macro_list.append(macro)

                macro_positon += 1
                macro_string = f"macro_{macro_positon}"

        print(f"Finished reading configuration file [{filename}]")

    except Exception as e:
        print(f"Failed to load configuration file [{filename}] - {e}")


def save_configuration(filename, settings, macro_list):

    try:
        #save config file
        print(f"Saving configuration file [{filename}]")

        config_data = {}
        for setting in settings:
            config_data[setting] = settings[setting].value

        macro_positon = 0
        for macro in macro_list:
            macro_string = f"macro_{macro_positon}"
            config_data[macro_string] = {}
            config_macro = config_data[macro_string]

            config_macro['name']        = macro['name']
            config_macro['filename']    = macro['filename']
            if 'play_hotkey' in macro:
                config_macro['play_hotkey'] = HotKeys.list_to_string(macro['play_hotkey'])
            if 'record_hotkey' in macro:
                config_macro['record_hotkey'] = HotKeys.list_to_string(macro['record_hotkey'])

            #set options
            for option_key, option_value in macro_options.items():
                if macro[option_key] != settings[option_value.value].value:
                    config_macro[option_key] = macro[option_key]

            macro_positon += 1

        with open(filename, 'w') as file:
            config_data = yaml.dump(config_data, file, sort_keys=False, default_flow_style=False)

    except Exception as e:
        print(f"Failed to save configuration file [{filename}] - {e}")