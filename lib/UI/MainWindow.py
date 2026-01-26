import time
import lib.Constants as Constants
import lib.HotKeys as HotKeys
import lib.Sequences as Sequences
import lib.ConfigFile as ConfigFile
import lib.Log as Log
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFontMetrics, QFont


class MainWindow(QMainWindow):
    def __init__(self, window_title, settings, macro_list, macro_mutex):
        super().__init__()

        self.settings = settings
        self.macro_list = macro_list
        self.macro_mutex = macro_mutex

        #set title
        self.setWindowTitle(window_title)

        #main layout
        self.mainLayoutBox = QVBoxLayout()

        #Config buttons
        self.configButtonLayout = QHBoxLayout()

        self.savePushButton = QPushButton("Save")
        self.savePushButton.setFixedHeight(50)
        self.savePushButton.pressed.connect(self.SaveButtonClick)
        self.configButtonLayout.addWidget(self.savePushButton)

        self.reloadPushButton = QPushButton("Reload")
        self.reloadPushButton.setFixedHeight(50)
        self.reloadPushButton.pressed.connect(self.ReloadButtonClick)
        self.configButtonLayout.addWidget(self.reloadPushButton)

        self.mainLayoutBox.addLayout(self.configButtonLayout)

        #macro table
        self.macroTable = QTableWidget()
        self.macroTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.macroTable.itemDoubleClicked.connect(self.onMacroDoubleClicked)

        #set columns
        macro_list_columns = []
        for column in Constants.MACRO_LIST_DATA:
            macro_list_columns.append(column)
        self.macroTable.setColumnCount(len(macro_list_columns))
        self.macroTable.setHorizontalHeaderLabels(macro_list_columns)

        index = 0
        for column_key, column_value in Constants.MACRO_LIST_DATA.items():
            self.macroTable.setColumnWidth(index, column_value['column_size'])
            index += 1

        #load macros
        self._loadMacroEntries()

        self.mainLayoutBox.addWidget(self.macroTable)

        #Macro buttons
        self.macroButtonLayout = QHBoxLayout()

        self.addPushButton = QPushButton("Add")
        self.addPushButton.setFixedHeight(50)
        self.addPushButton.pressed.connect(self.AddButtonClick)
        self.macroButtonLayout.addWidget(self.addPushButton)

        self.removePushButton = QPushButton("Remove")
        self.removePushButton.setFixedHeight(50)
        self.removePushButton.pressed.connect(self.RemoveButtonClick)
        self.macroButtonLayout.addWidget(self.removePushButton)

        self.mainLayoutBox.addLayout(self.macroButtonLayout)

        #log box
        self.listViewLog = QListWidget()
        self.listViewLog.setFixedHeight(150)

        self.mainLayoutBox.addWidget(self.listViewLog)

        font = self.listViewLog.font()
        font_metrics = QFontMetrics(font)
        self.text_height = font_metrics.boundingRect("X").height() + 1

        Log.set_output(self._writeLog)
        Log.dump_buffer()

        widget = QWidget()
        widget.setLayout(self.mainLayoutBox)
        self.setGeometry(300, 300, 975, 600)
        self.setCentralWidget(widget)
        self.show()


    def SaveButtonClick(self):
        with self.macro_mutex:
            ConfigFile.save_configuration(Constants.CONFIG_FILENAME, self.settings, self.macro_list)


    def ReloadButtonClick(self):
        with self.macro_mutex:
            ConfigFile.read_configuration(Constants.CONFIG_FILENAME, self.settings, self.macro_list)

        self._loadMacroEntries()


    def AddButtonClick(self):
        try:
            self.macroTable.cellChanged.disconnect()

            with self.macro_mutex:
                macro = {
                    'name'                      : "new macro",
                    'filename'                  : "",
                    'sequence'                  : [],
                    'lastplay'                  : time.time(),
                    'playback_delay'            : self.settings['default_playback_delay'].value,
                    'listen_during_playback'    : self.settings['default_listen_during_playback'].value,
                    'record_delay'              : self.settings['default_record_delay'].value,
                    'record_mouse_movement'     : self.settings['default_record_mouse_movement'].value,
                    'record_mouse_fps'          : self.settings['default_record_mouse_fps'].value,
                    'playback_speed'            : self.settings['default_playback_speed'].value,
                    'cooldown'                  : self.settings['default_macro_cooldown'].value,
                }

                new_index = len(self.macro_list)
                self.macro_list.append(macro)
                self.macroTable.setRowCount(new_index + 1)
                self._loadMacroInfo(new_index)

        except Exception as e:
            Log.e(f"Error addMacroEntry - {e}")

        self.macroTable.cellChanged.connect(self.onMacroCellChanged)


    def RemoveButtonClick(self):
        try:
            self.macroTable.cellChanged.disconnect()

            # Get a list of selected row indices
            selected_rows = set()
            for item in self.macroTable.selectedItems():
                selected_rows.add(item.row())

            # Convert to a list and sort in reverse order
            sorted_rows = sorted(list(selected_rows), reverse=True)

            # Delete rows
            with self.macro_mutex:
                for row in sorted_rows:
                    self.macroTable.removeRow(row)
                    del self.macro_list[row]

        except Exception as e:
            Log.e(f"Error addMacroEntry - {e}")

        self.macroTable.cellChanged.connect(self.onMacroCellChanged)


    def loadMacroInfo(self, row):
        try:
            self.macroTable.cellChanged.disconnect()
            with self.macro_mutex:
                self._loadMacroInfo(row)

        except Exception as e:
            Log.e(f"Error loadMacroInfo - {e}")

        self.macroTable.cellChanged.connect(self.onMacroCellChanged)


    def onMacroDoubleClicked(self, item):
        try:
            column_item = self.macroTable.item(item.row(), item.column())
            column_key = self.macroTable.horizontalHeaderItem(item.column()).text()
            column_value = Constants.MACRO_LIST_DATA[column_key]
            action_type = column_value['on_dbl_click']

            with self.macro_mutex:
                macro = self.macro_list[item.row()]
                if action_type == Constants.ListAction.LOAD_SEQUENCE_DIALOG:
                    filename = QFileDialog.getOpenFileName(self, "Open Sequence", "", "Json (*.json)")

                    Log.i(f"Setting [{macro['name']}] - {column_value['macro_key']} to {filename[0]}")

                    macro[column_value['macro_key']] = filename[0]
                    macro['sequence'] = Sequences.load_sequence(filename[0])

        except Exception as e:
            Log.e(f"Error onMacroDoubleClicked - {e}")

        self.loadMacroInfo(item.row())


    def onMacroCellChanged(self, row, column):
        try:
            column_str = self.macroTable.item(row, column).text()
            column_key = self.macroTable.horizontalHeaderItem(column).text()
            column_value = Constants.MACRO_LIST_DATA[column_key]
            action_type = column_value['on_change']
            var_type = column_value['var_type']

            #convert variable type as needed
            if var_type == Constants.VariableType.INT:
                column_str = int(column_str)

            elif var_type == Constants.VariableType.FLOAT:
                column_str = float(column_str)

            elif var_type == Constants.VariableType.BOOLEAN:
                column_str = True if column_str.lower() == 'true' else False

            with self.macro_mutex:
                macro = self.macro_list[row]
                Log.i(f"Setting [{macro['name']}] - {column_value['macro_key']} to {column_str}")
                if action_type == Constants.ListAction.NONE:
                    macro[column_value['macro_key']] = column_str

                elif action_type == Constants.ListAction.LOAD_HOTKEY:
                    hotkey_string = HotKeys.string_to_list(column_str)

                    if hotkey_string == "":
                        if column_value['macro_key'] in macro:
                            del macro[column_value['macro_key']]

                    else:
                        macro[column_value['macro_key']] = HotKeys.string_to_list(column_str)

                elif action_type == Constants.ListAction.LOAD_SEQUENCE:
                    macro[column_value['macro_key']] = column_str
                    macro['sequence'] = Sequences.load_sequence(column_str)

        except Exception as e:
            Log.e(f"Error onMacroCellChanged - {e}")

        self.loadMacroInfo(row)


    def _loadMacroInfo(self, row):
        macro = self.macro_list[row]
        index = 0
        for column_key, column_value in Constants.MACRO_LIST_DATA.items():
            column_str = ""
            if column_value['macro_key'] in macro:
                if isinstance(macro[column_value['macro_key']], list):
                    column_str = HotKeys.list_to_string(macro[column_value['macro_key']])

                else:
                    column_str = str(macro[column_value['macro_key']])

            current_item = self.macroTable.item(row, index)
            if current_item is not None:
                current_item.setText(column_str)
                
            else:
                self.macroTable.setItem(row, index, QTableWidgetItem(column_str))

            index += 1


    def _loadMacroEntries(self):
        try:
            try:
                self.macroTable.cellChanged.disconnect()

            except:
                pass

            with self.macro_mutex:
                self.macroTable.setRowCount(len(self.macro_list))
                for i in range(len(self.macro_list)):
                    self._loadMacroInfo(i)

        except Exception as e:
            Log.e(f"Error _loadMacroEntries - {e}")

        self.macroTable.cellChanged.connect(self.onMacroCellChanged)


    def _writeLog(self, out):
        item = QListWidgetItem()
        item.setText(out)
        item.setSizeHint(QSize(10000, self.text_height))

        self.listViewLog.addItem(item)
        self.listViewLog.scrollToBottom()