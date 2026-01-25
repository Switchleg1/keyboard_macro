import lib.Constants as Constants
import lib.HotKeys as HotKeys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView


class MainWindow(QMainWindow):
    def __init__(self, window_title, macro_list, macro_mutex):
        super().__init__()

        self.macro_list = macro_list
        self.macro_mutex = macro_mutex

        #set title
        self.setWindowTitle(window_title)

        #main layout
        self.mainLayoutBox = QVBoxLayout()

        #macro table
        self.macroTable = QTableWidget()
        self.macroTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

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

        for macro in macro_list:
            self.addMacroEntry(macro)

        self.mainLayoutBox.addWidget(self.macroTable)

        widget = QWidget()
        widget.setLayout(self.mainLayoutBox)
        self.setGeometry(300, 300, 975, 500)
        self.setCentralWidget(widget)
        self.show()


    def addMacroEntry(self, macro):
        self.macroTable.setRowCount(self.macroTable.rowCount() + 1)

        index = 0
        for column_key, column_value in Constants.MACRO_LIST_DATA.items():
            column_str = ""
            if column_value['macro_key'] in macro:
                if isinstance(macro[column_value['macro_key']], list):
                    column_str = HotKeys.list_to_string(macro[column_value['macro_key']])

                else:
                    column_str = macro[column_value['macro_key']]

            self.macroTable.setItem(self.macroTable.rowCount() - 1, index, QTableWidgetItem(column_str))
            index += 1