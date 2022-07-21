from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import (QDialog)
from PyQt5.QtGui import *
import commondata as cd
import json


class Language(QDialog):
    lang = None
    form_parent = None

    def __init__(self, form_parent):
        super().__init__()
        self.form_parent = form_parent
        # self.setStyleSheet('background-color: beige;')
        self.setFont(QtGui.QFont('Arial', 12))
        self.setWindowTitle(cd.get_text('Choice of language for the program', key='main', id_text=16))
# кнопки управления
        layout_button = QtWidgets.QHBoxLayout()
        self.choice = QtWidgets.QPushButton(cd.get_text('Выбрать', key='main', id_text=17))
        self.choice.setToolTip(cd.get_text('Установить выбранный язык', key='main', id_text=19))
        self.choice.clicked.connect(self.choice_click)
        layout_button.addWidget(self.choice)

        self.exit = QtWidgets.QPushButton(cd.get_text('Закрыть', key='main', id_text=18))
        self.exit.setToolTip(cd.get_text('Закрыть форму без изменения языка', key='main', id_text=20))
        self.exit.clicked.connect(self.exit_click)
        layout_button.addWidget(self.exit)
# контейнер для дерева
        layout_table = QtWidgets.QHBoxLayout()
        self.root_model = QStandardItemModel()
        self.table = QtWidgets.QTreeView()
        self.table.setRootIsDecorated(True)
        self.table.setAlternatingRowColors(True)
        self.table.setIndentation(20)
        self.table.setUniformRowHeights(False)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)
        self.table.setModel(self.root_model)
        self.table.header().setDefaultSectionSize(120)
        self.table.selectionModel().selectionChanged.connect(self.row_change)
        header = self.table.header()
        header.setHighlightSections(True)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        header.setStretchLastSection(False)  # последняя строке не занимает все свободное место
        self.table.setSelectionBehavior(1)  # выделяется одна строка целиком
        self.root_model.setHorizontalHeaderLabels(
            ['№№', 'ID', 'Name'])
        layout_table.addWidget(self.table)
# финальный аккорд
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layout_button)
        layout.addLayout(layout_table)
        self.setLayout(layout)

        self.set_geometry()
        self.show_data()
        self.table.setFocus()

    def choice_click(self):
        # выбран язык
        if self.lang != cd.app_lang:
            cd.app_lang = self.lang
            cd.load_texts(cd.app_lang)
            cd.send_evt(cd.evt_change_language, self.form_parent)  # изменили язык
            cd.settings.setValue("app_language", cd.app_lang)  # сразу запомнить выбранный язык
            cd.settings.sync()
        self.close()

    def exit_click(self):
        # закрыть без выбора языка
        self.close()

    def closeEvent(self, evt):
        cd.settings.setValue("choice_language", self.geometry())
        cd.settings.sync()

    def set_geometry(self):
        if cd.settings.contains("choice_language"):
            self.setGeometry(cd.settings.value("choice_language"))
        else:
            self.resize(300, 200)

    def row_change(self, new, old):
        try:
            self.selection_change(self.root_model.index(self.table.selectionModel().selectedRows()[0].row(), 0))
        except:
            pass

    def selection_change(self, index):
        ind = index.sibling(index.row(), 1)
        self.lang = self.root_model.data(ind)

    def show_data(self):
        self.root_model.setRowCount(0)  # сбросить таблицу
        # self.table.setColumnHidden(8, True)
        filename = 'languages/texts.json'
        try:
            f = open(filename, 'rt', encoding='utf-8')
            with f:
                txt_standard = json.loads(f.read())
            arow = 0
            if "languages" in txt_standard:
                txt_standard = txt_standard["languages"]
                for unit in txt_standard:
                    id = unit['id']
                    txt = unit['text']
                    row = list()
                    row.append(QStandardItem(str(arow + 1)))
                    row.append(QStandardItem(id))
                    row.append(QStandardItem(txt))
                    cd.row_only_read(row, [])
                    self.root_model.appendRow(row)
                    cd.set_align(self.table, arow, [2])
                    arow += 1
                # ширина колонок по содержимому
                cd.set_width_columns(self.table, [], increment=20, last_column=False)
                ind = cd.get_index_row_in_table(self.root_model, cd.app_lang, 1)
                self.table.setCurrentIndex(ind)  # сделать строку выбранной
        except Exception as err:
            cd.show_message(None, f"{err}", 'Error', onlyok=True)
