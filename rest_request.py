import commondata
from PyQt5.QtWidgets import (QLabel, QPushButton, QWidget, QTextEdit, QLineEdit, QScrollArea, QComboBox, QFileDialog)
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import commondata as cd
import json
import os
import time


arr = ([
    'factions.json #GET # список фракций в созывах ГД',
    'deputies.json #GET',
    'search.json #GET',
    'federal-organs.json #GET # федеральные органы в разные периоды',
    'committees.json #GET # список комитетов',
    'topics.json #GET # список тематических блоков',
    'classes.json #GET # отрасли законодательства',
    "instances.json #GET # список инстанций рассмотрения",
    'periods.json #GET # созывы и сессии'
])


class TShowResult(QWidget):
    exist = False
    mes = ''
    length_request = None
    len_array = None
    row_count = None
    t_read = None
    select_directory = ''
    select_file = ''

    def __init__(self, parent):
        super(QWidget, self).__init__()

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout1 = QtWidgets.QVBoxLayout()  # для параметров
        layout2 = QtWidgets.QVBoxLayout()  # для ответа
        scrollparams = QScrollArea(self.splitter)
        content_params = QtWidgets.QWidget()
        scrollparams.setWidget(content_params)
        scrollparams.setWidgetResizable(True)
        scrollparams.setLayout(layout1)
        self.send_button = QPushButton()
        self.send_button.clicked.connect(self.send_command_click)  # нажата кнопка ПОСЛАТЬ
        self.take_token = QPushButton()
        self.take_token.setText('')
        self.take_token.clicked.connect(self.take_token_click)  # взять токен и положить в поле для токена
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.send_button, 10)
        layout.addWidget(self.take_token)
        layout1.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        self.label_token = QLabel('')
        layout.addWidget(self.label_token)
        self.token = QTextEdit(cd.api_token)
        layout.addWidget(self.token)
        layout1.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        self.label_directive = QLabel('')
        layout.addWidget(self.label_directive)
        self.combo_dirs = QComboBox()
        self.combo_dirs.addItem('GET')
        self.combo_dirs.addItem('POST')
        self.combo_dirs.addItem('PATCH')
        self.combo_dirs.addItem('PUT')
        self.combo_dirs.addItem('DELETE')
        if cd.settings.contains("rest_dir"):
            self.combo_dirs.setCurrentText(cd.settings.value("rest_dir"))
        else:
            self.combo_dirs.setCurrentIndex(0)
        layout.addWidget(self.combo_dirs, 10)
        layout1.addLayout(layout, 2)
        layout = QtWidgets.QHBoxLayout()
        self.label_language = QLabel('')
        layout.addWidget(self.label_language)
        self.combo_lang = QComboBox()
        self.combo_lang.addItem('ru')
        self.combo_lang.addItem('en')
        self.combo_lang.addItem('il')
        self.combo_lang.addItem('')
        if cd.settings.contains("rest_lang"):
            self.combo_lang.setCurrentText(cd.settings.value("rest_lang"))
        else:
            self.combo_lang.setCurrentIndex(0)
        layout.addWidget(self.combo_lang, 10)
        self.save_button = QPushButton(cd.iconSave, '')
        self.save_button.clicked.connect(self.save_click)  # нажата кнопка ПОСЛАТЬ
        layout.addWidget(self.save_button, 2)
        self.file_button = QPushButton(cd.iconOpen, '')
        self.file_button.clicked.connect(self.file_click)  # нажата кнопка ПОСЛАТЬ
        layout.addWidget(self.file_button, 2)
        layout1.addLayout(layout, 2)

        layout = QtWidgets.QHBoxLayout()
        self.label_command = QLabel('')
        layout.addWidget(self.label_command)
        self.text_command = QLineEdit()
        self.text_command.setClearButtonEnabled(True)
        self.completer = QtWidgets.QCompleter(arr)
        self.completer.setMaxVisibleItems(20)
        self.completer.activated.connect(self.completer_activate)
        self.text_command.setCompleter(self.completer)
        # self.text_command.returnPressed.connect(self.send_command_click) # ввод текста в поле закончен символом RETURN
        # self.text_command.textChanged.connect(self.text_command_changed)

        if cd.settings.contains("rest_command"):
            self.text_command.setText(cd.settings.value("rest_command"))
        layout.addWidget(self.text_command)
        layout1.addLayout(layout, 2)
        layout = QtWidgets.QHBoxLayout()
        label = QLabel('Body:')
        layout.addWidget(label)
        self.body = QTextEdit()
        layout.addWidget(self.body, 10)
        if cd.settings.contains("rest_body_text"):
            self.body.setText(cd.settings.value("rest_body_text"))
        layout1.addLayout(layout, 10)
        self.errors = QLabel('')
        layout.addWidget(self.errors)

        scrolltable = QScrollArea(self.splitter)
        layout = QtWidgets.QHBoxLayout()
        self.status_code = QLabel('Status_code:')
        layout.addWidget(self.status_code)
        layout2.addLayout(layout)
        content_table = QtWidgets.QWidget()
        scrolltable.setWidget(content_table)
        scrolltable.setWidgetResizable(True)
        scrolltable.setLayout(layout2)
        self.label_answer = QLabel('')
        layout2.addWidget(self.label_answer)
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        layout2.addWidget(self.text_result, 10)
        layout = QtWidgets.QHBoxLayout()
        self.statusbar = QLabel('')
        layout.addWidget(self.statusbar)
        self.time_calc = QLabel('')
        layout.addWidget(self.time_calc)
        layout2.addLayout(layout)

        # ширина левой и правой части из settings
        w = 800
        h = 400
        try:
            if cd.settings.contains("rest_splitter_width"):
                w = max(100, int(cd.settings.value("rest_splitter_width", 800)))
            if cd.settings.contains("rest_splitter_height"):
                h = max(100, int(cd.settings.value("rest_splitter_height", 400)))
        except Exception as e:
            st = " Error: " + f"{e}"
            QtWidgets.QMessageBox.critical(None, "cd.settings", st,
                                           defaultButton=QtWidgets.QMessageBox.Ok)
        self.splitter.setSizes([w, h])
        if cd.settings.contains("request_directory"):
            self.select_directory = cd.settings.value("request_directory", '')
        if cd.settings.contains("request_file"):
            self.select_file = cd.settings.value("request_file", '')

        # все соберем вместе
        self.splitter.addWidget(scrollparams)
        self.splitter.addWidget(scrolltable)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.splitter, 10)
        parent.setLayout(self.layout)
        self.exist = True
        self.change_language()

    def change_language(self):
        self.send_button.setText(cd.get_text('Send request', id_text=1, key='rest'))
        self.take_token.setText(cd.get_text('Токен', id_text=2, key='rest'))
        self.label_token.setText(cd.get_text('Токен', id_text=2, key='rest') + ':')
        self.label_directive.setText(cd.get_text('Директива', id_text=3, key='rest') + ':')
        self.label_language.setText(cd.get_text('Язык', id_text=4, key='rest') + ':')
        self.save_button.setText(cd.get_text('Сохранить в файл', id_text=5, key='rest'))
        self.save_button.setToolTip(cd.get_text("Выбор файла для BODY", id_text=12, key='rest'))
        self.file_button.setText(cd.get_text('Загрузить из файла', id_text=6, key='rest'))
        self.file_button.setToolTip(cd.get_text("Выбор файла для BODY", id_text=11, key='rest'))
        self.label_command.setText(cd.get_text('Запрос', id_text=7, key='rest') + ':')
        self.text_command.setPlaceholderText(
            cd.get_text('Введите текст команды для посылки ее в адрес RESTProxy', id_text=8, key='rest'))
        self.show_status_bar()
        if self.t_read is not None:
            self.time_calc.setText(cd.get_text('T запроса= %.3f сек', id_text=25, key='main') % self.t_read)
        self.label_answer.setText(cd.get_text('Ответ', id_text=13, key='rest') + ':')

    def customEvent(self, evt):
        if evt.type() == cd.StatusOperation.idType:  # изменение состояния соединения PROXY
            n = evt.get_data()
            # if n == cd.evt_refresh_connect:
            #     self.token.setText(cd.api_token)
            if n == cd.evt_change_language:
                self.change_language()

    # закрыть форму
    def closeEvent(self, evt):
        spis = self.splitter.sizes()
        cd.settings.setValue("rest_splitter_width", spis[0])
        cd.settings.setValue("rest_splitter_height", spis[1])
        cd.settings.setValue("rest_body_text", self.body.toPlainText())
        cd.settings.setValue("rest_command", self.text_command.text())
        cd.settings.setValue("rest_dir", self.combo_dirs.currentText())
        cd.settings.setValue("rest_lang", self.combo_lang.currentText())

    def load_from_file(self, filename):
        try:
            f = open(filename, 'r', encoding='utf-8-sig')
            with f:
                data = f.read()
                self.body.setText(data)
        except Exception:
            try:
                f = open(filename, 'r', encoding='ansi')
                with f:
                    data = f.read()
                    self.body.setText(data)
                self.errors.setText('')
            except Exception as e:
                self.errors.setText(cd.get_text('Ошибка', id_text=4, key='main') + ' ' + filename + '\n' + f"{e}")

    def file_click(self):
        dialog = QFileDialog(caption=cd.get_text("Выбор файла для BODY", id_text=11, key='rest'))
        if self.select_directory:
            dialog.setDirectory(self.select_directory)
        if self.select_file:
            dialog.FileName = self.select_file
            dialog.selectFile(self.select_file)
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            self.select_directory = os.path.dirname(filename)
            self.select_file = filename
            cd.settings.setValue("request_directory", self.select_directory)
            cd.settings.setValue("request_file", self.select_file)
            cd.settings.sync()
            self.load_from_file(filename)

    def save_click(self):
        dialog = QFileDialog(caption=cd.get_text("Выбор файла для экспорта BODY", id_text=12, key='rest'))
        dialog.setDefaultSuffix('json')
        if self.select_directory:
            dialog.setDirectory(self.select_directory)
        if self.select_file:
            dialog.FileName = self.select_file
            dialog.selectFile(self.select_file)
        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            self.select_directory = os.path.dirname(filename)
            self.select_file = filename
            cd.settings.setValue("request_directory", self.select_directory)
            cd.settings.setValue("request_file", self.select_file)
            cd.settings.sync()
            self.save_to_file(filename)

    def save_to_file(self, filename):
        try:
            f = open(filename, 'w', encoding='utf-8')
            with f:
                f.write(self.body.toPlainText())
            self.errors.setText('')
        except Exception as e:
            self.errors.setText(cd.get_text('Ошибка', id_text=4, key='main') + ' ' + filename + '\n' + f"{e}")

    def completer_activate(self, st):
        if self.exist:
            self.exist = False
            self.mes, st = cd.getpole(st, '#')
            self.text_command.setText(self.mes)
            directive, txt = cd.getpole(st, '#')
            directive = directive.strip()
            if directive != '':
                self.combo_dirs.setCurrentText(directive)
            txt = txt.strip()
            try:
                if txt != '':
                    self.body.setText(json.dumps(json.loads(txt), sort_keys=False, indent=4, ensure_ascii=False))
            except:
                self.body.setText(txt)
            self.text_command.setText(self.mes)
            self.exist = True

    # def text_command_changed(self):
    #     if self.exist:
    #         self.mes = self.text_command.text()
    #         self.exist = False
            # self.mes = self.mes.replace('token=', 'token=' + commondata.token)
            # self.text_command.setText(self.mes)
            # print(self.mes)
            # self.exist = True

    def send_command_click(self):
        if not self.exist:
            return
        QApplication.setOverrideCursor(Qt.BusyCursor)  # курсор ожидания
        try:
            self.time_calc.setText(cd.get_text('выполнение запроса ...', id_text=27, key='main'))
            self.time_calc.repaint()
            t_begin = time.time()
            st = self.text_command.text().strip()
            st = st.split(' #')[0].strip()
            # st = st.strip().replace('token_need=', 'token=' + commondata.api_token)
            self.save_to_file('tmp')
            # if 'token=' not in st:
            #     if '?' in st:
            #         st = st + '&token=' + cd.api_token
            #     else:
            #         st = st + '?token=' + cd.api_token
            params = self.body.toPlainText().split('\n')

            answer, result, status_code = cd.send_rest_full(
                st,
                directive=self.combo_dirs.currentText(),
                params=params,
                # lang=self.combo_lang.currentText(),
                show_error=False)
                # tokenuser=self.token.toPlainText())
            self.t_read = time.time() - t_begin
            self.time_calc.setText(cd.get_text('T запроса = %.3f сек', id_text=25, key='main') % self.t_read)
            self.show_data(answer)
            self.status_code.setText(str(status_code) + ' (' + self.combo_dirs.currentText() + ') ' + st)
        except:
            pass
        QApplication.restoreOverrideCursor()  # восстановление курсора
        self.load_from_file('tmp')

    def show_data(self, txt):
        try:
            if txt[0] == '"':
                txt = txt[1:]
                txt = txt[:-1]
            else:
                d = json.loads(txt)
                self.len_array = None
                if type(d) == list:
                    self.len_array = len(d)
                else:
                    self.len_array = None
                txt = json.dumps(d, indent=4, ensure_ascii=False)
        except Exception as e:
            try:
                txt = txt.replace('\n', ' ')
                d = json.loads(txt)
                self.len_array = None
                if type(d) == list:
                    self.len_array = len(d)
                else:
                    self.len_array = None
                txt = json.dumps(d, indent=4, ensure_ascii=False)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    None, "cd.settings", cd.get_text('Ошибка', id_text=4, key='main') + '\n' + f"{e}",
                    defaultButton=QtWidgets.QMessageBox.Ok)
        self.text_result.setText(txt.strip())
        self.length_request = len(txt)
        self.row_count = self.text_result.document().lineCount()
        self.show_status_bar()

    def show_status_bar(self):
        st = ''
        if self.length_request is not None:
            st = cd.get_text('Длина', id_text=2, key='data') + '= ' + cd.str1000(self.length_request) + '; '
        if self.row_count is not None:
            st = st + cd.get_text('Строк', id_text=9, key='rest') + '= ' + cd.str1000(self.row_count) + '; '
        if self.len_array is not None:
            st = st + cd.get_text('Элементов в массиве', id_text=10, key='rest') + '= ' + cd.str1000(self.len_array)
        self.statusbar.setText(st)

    def take_token_click(self):
        self.token.setText(cd.api_token)
