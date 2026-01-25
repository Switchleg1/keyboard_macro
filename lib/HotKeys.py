import json


def string_to_list(hotkey_string):
    hotkey_list = hotkey_string.split('|')

    for x in range(len(hotkey_list)):
        hotkey_list[x] = hotkey_list[x].split('+')

    return hotkey_list


def list_to_string(hotkey_list):
    hotkey_string = ""

    for hotkey in hotkey_list:
        if hotkey_string != "":
            hotkey_string += '|'

        isFirstKey = True
        for key in hotkey:
            if isFirstKey == False:
                hotkey_string += '+'

            hotkey_string += key
            isFirstKey = False

    return hotkey_string