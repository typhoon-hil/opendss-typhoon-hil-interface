import importlib

pyside6_exists = importlib.find_loader("PySide6")
if pyside6_exists:
    from PySide6 import QtCore, QtWidgets
else:
    from PyQt5 import QtCore, QtWidgets


class Ui_header_and_column(object):
    def setupUi(self, header_and_column):
        header_and_column.setObjectName("header_and_column")
        header_and_column.resize(213, 147)
        header_and_column.setMinimumSize(QtCore.QSize(213, 147))
        header_and_column.setMaximumSize(QtCore.QSize(213, 147))
        self.gridLayout = QtWidgets.QGridLayout(header_and_column)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.combobox_column = QtWidgets.QComboBox(header_and_column)
        self.combobox_column.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.combobox_column.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.combobox_column.setObjectName("combobox_column")
        self.gridLayout_2.addWidget(self.combobox_column, 1, 1, 1, 1)
        self.label_column = QtWidgets.QLabel(header_and_column)
        self.label_column.setObjectName("label_column")
        self.gridLayout_2.addWidget(self.label_column, 1, 0, 1, 1)
        self.checkbox_headers = QtWidgets.QCheckBox(header_and_column)
        self.checkbox_headers.setObjectName("checkbox_headers")
        self.gridLayout_2.addWidget(self.checkbox_headers, 0, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_ok = QtWidgets.QPushButton(header_and_column)
        self.button_ok.setObjectName("button_ok")
        self.horizontalLayout.addWidget(self.button_ok)
        self.button_cancel = QtWidgets.QPushButton(header_and_column)
        self.button_cancel.setObjectName("button_cancel")
        self.horizontalLayout.addWidget(self.button_cancel)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(header_and_column)
        QtCore.QMetaObject.connectSlotsByName(header_and_column)

    def retranslateUi(self, header_and_column):
        _translate = QtCore.QCoreApplication.translate
        header_and_column.setWindowTitle(_translate("header_and_column", "Load from file"))
        self.label_column.setText(_translate("header_and_column", "Select Column"))
        self.checkbox_headers.setText(_translate("header_and_column", "File has headers"))
        self.button_ok.setText(_translate("header_and_column", "OK"))
        self.button_cancel.setText(_translate("header_and_column", "Cancel"))


class HeaderAndColumn(QtWidgets.QDialog, Ui_header_and_column):

    def __init__(self, headers):
        super().__init__()
        self.setupUi(self)

        self.has_headers = False
        self.selected_column = ""

        self.headers = headers
        self.fill_data()

        self.checkbox_headers.clicked.connect(self.fill_data)

        self.button_ok.clicked.connect(self.returned_values)
        self.button_cancel.clicked.connect(self.reject)

    def fill_data(self):
        num_columns = len(self.headers)

        self.combobox_column.clear()

        if self.checkbox_headers.isChecked():
            self.combobox_column.addItems(self.headers)
        else:
            self.combobox_column.addItems([str(n) for n in range(1, num_columns + 1)])

    def returned_values(self):

        self.has_headers = self.checkbox_headers.isChecked()
        self.selected_column = str(self.combobox_column.currentIndex() + 1)

        self.accept()
