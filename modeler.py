from PyQt5 import (QtWidgets, QtCore, QtGui)
from PyQt5.QtWidgets import (QWidget, QLabel, QTabWidget, QCheckBox, QPushButton, QApplication, QProgressBar,
                             QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
import time
import commondata as cd
import os


class TModeler(QWidget):
    form_parent = None
    exist = False

    def __init__(self, parent):
        super(QWidget, self).__init__()
        self.form_parent = parent
        self.setFont(self.form_parent.font())

        # layout_button = QtWidgets.QHBoxLayout()
        # self.show_table = QCheckBox('Table')
        # layout_button.addWidget(self.show_table)

        # layout1 = QtWidgets.QVBoxLayout()
        # layout1.addLayout(layout_button)
        # финальный аккорд
        # self.setLayout(layout1)

    def change_language(self):
        pass
