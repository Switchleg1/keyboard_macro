from enum import Enum

APP_VERSION                     = "v1.1"
CONFIG_FILENAME                 = "config.yaml"
DEFAULT_PLAYBACK_DELAY          = 0.05
DEFAULT_PLAY_SIZE               = 3
DEFAULT_RECORD_SIZE             = 3
DEFAULT_USE_KEYBOARD            = True
DEFAULT_USE_MOUSE               = True
DEFAULT_USE_MOUSE_WHEEL         = True
DEFAULT_KEY_TIMEOUT             = 3
DEFAULT_MACRO_COOLDOWN          = 1.0
DEFAULT_LISTEN_PLAYBACK         = True
DEFAULT_RECORD_DELAY            = False
DEFAULT_MOUSE_MOVEMENT          = False
DEFAULT_MOUSE_FPS               = 30
DEFAULT_PLAYBACK_SPEED          = 1.0
DEFAULT_USE_GUI                 = True
DEFAULT_START_MINIMIZE          = False


class ListAction(Enum):
    NONE                    = 0
    LOAD_HOTKEY             = 1
    LOAD_SEQUENCE           = 2
    LOAD_SEQUENCE_DIALOG    = 3


class VariableType(Enum):
    STRING                  = 0
    INT                     = 1
    FLOAT                   = 2
    BOOLEAN                 = 3


MACRO_LIST_DATA                 = {
    'Name'                      : {
        'column_size'           : 175,
        'macro_key'             : 'name',
        'on_change'             : ListAction.NONE,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.STRING,
    },
    'Play HotKey'               : {
        'column_size'           : 175,
        'macro_key'             : 'play_hotkey',
        'on_change'             : ListAction.LOAD_HOTKEY,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.STRING,
    },
    'Rec Hotkey'                : {
        'column_size'           : 175,
        'macro_key'             : 'record_hotkey',
        'on_change'             : ListAction.LOAD_HOTKEY,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.STRING,
    },
    'Filename'                  : {
        'column_size'           : 400,
        'macro_key'             : 'filename',
        'on_change'             : ListAction.LOAD_SEQUENCE,
        'on_dbl_click'          : ListAction.LOAD_SEQUENCE_DIALOG,
        'var_type'              : VariableType.STRING,
    },
    'Listen During Playback'    : {
        'column_size'           : 125,
        'macro_key'             : 'listen_during_playback',
        'on_change'             : ListAction.NONE,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.BOOLEAN,
    },
    'Playback Delay'            : {
        'column_size'           : 90,
        'macro_key'             : 'playback_delay',
        'on_change'             : ListAction.NONE,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.FLOAT,
    },
    'Record Delay'              : {
        'column_size'           : 80,
        'macro_key'             : 'record_delay',
        'on_change'             : ListAction.NONE,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.BOOLEAN,
    },
    'Record Mouse Movement'     : {
        'column_size'           : 150,
        'macro_key'             : 'record_mouse_movement',
        'on_change'             : ListAction.NONE,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.BOOLEAN,
    },
    'Record Mouse FPS'          : {
        'column_size'           : 110,
        'macro_key'             : 'record_mouse_fps',
        'on_change'             : ListAction.NONE,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.BOOLEAN,
    },
    'Playback Speed'            : {
        'column_size'           : 90,
        'macro_key'             : 'playback_speed',
        'on_change'             : ListAction.NONE,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.FLOAT,
    },
    'Cooldown'                  : {
        'column_size'           : 80,
        'macro_key'             : 'cooldown',
        'on_change'             : ListAction.NONE,
        'on_dbl_click'          : ListAction.NONE,
        'var_type'              : VariableType.FLOAT,
    }
}