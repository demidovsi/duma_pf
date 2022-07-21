from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QApplication, QFontDialog, QTabWidget
from PyQt5.QtWidgets import QLabel, QStyle
from PyQt5.QtGui import QIcon
import time
import commondata as cd
import clock
import rest_request
import pagecontrol
import choos_language


class Form(QMainWindow):
    modeler = None
    clock = None
    show_rest = None

    def __init__(self):
        super().__init__()
        self.setFont(QtGui.QFont('Arial', 9))
        cd.tform_handle = self

        cd.icon_font = QIcon()
        cd.icon_font.addFile('icons/font.bmp')
        cd.iconSave = self.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton)
        cd.iconUp = self.style().standardIcon(QtWidgets.QStyle.SP_ArrowUp)
        cd.iconOpen = self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton)
        cd.iconDown = self.style().standardIcon(QtWidgets.QStyle.SP_ArrowDown)

        self.labelTime = QLabel('Time')
        self.labelTime.setStyleSheet("color: blue")
        self.labelTime.setFont(self.font())
        self.statusBar().addPermanentWidget(self.labelTime)  # постоянная часть справа

        if cd.settings.contains("DumaFont"):
            self.setFont(cd.settings.value("DumaFont"))
# запустим таймер для вывода времени
        self.clock = clock.ClockThread(1, self.labelTime)
        self.clock.start()
# выбрать фонт
        self.choosfont = QAction(cd.icon_font, '', self)
        self.choosfont.setShortcut('Ctrl+F')
        self.choosfont.triggered.connect(self.choice_font)
# сменить язык
        self.language = QAction('', self)
        self.language.setShortcut('Ctrl+L')
        self.language.triggered.connect(self.language_click)
# использовать звук
        self.with_sound = QAction('', self, checkable=True)
        self.with_sound.setChecked(2)
        self.with_sound.setShortcut('Ctrl+S')
        self.with_sound.triggered.connect(self.with_sound_click)
# окончание программы
        self.exit_action = QAction(self.style().standardIcon(QStyle.SP_DialogCancelButton), '', self)
        self.exit_action.setShortcut('Alt+X')
        self.exit_action.triggered.connect(self.close)
# меню
        menubar = self.menuBar()
        self.menuconsol = menubar.addMenu('')
        self.menuconsol.addAction(self.choosfont)  # выбрать фонт
        self.menuconsol.addAction(self.language)  # выбрать язык
        self.menuconsol.addAction(self.with_sound)  # исползовать звук
        self.menuconsol.addSeparator()
        self.menuconsol.addAction(self.exit_action)  # menuStop

# запомненные настройки
        if cd.settings.contains("Duma"):
            self.setGeometry(cd.settings.value("Duma"))
        else:
            self.resize(cd.width_form, cd.height_form)
        if cd.settings.contains("Font"):
            self.setFont(cd.settings.value("Font"))
        if cd.settings.contains("with_sound"):
            cd.with_sound = cd.settings.value("with_sound") == '1'
        if cd.with_sound:
            self.with_sound.setChecked(2)
        else:
            self.with_sound.setChecked(0)
# основная форма
        self.widget = QWidget()
        self.page_control = pagecontrol.PageControl(self.widget, QTabWidget.West)
        # self.page_control.tabs.currentChanged.connect(self.pageControlChanged)
# Страница "RESTProxy"
        self.tabRest = self.page_control.addTab('RESTProxy')
        self.show_rest = rest_request.TShowResult(self.tabRest)

        self.setCentralWidget(self.page_control)
        self.set_font()
        self.change_language()
        self.show()

    def change_language(self):
        self.choosfont.setText(cd.get_text('Font', key='common', id_text=1))
        self.language.setText(cd.get_text("Choice of language", key='main', id_text=15))
        self.with_sound.setText(cd.get_text('использовать звуки', key='main', id_text=1))
        self.exit_action.setText(cd.get_text('Закончить', key='common', id_text=2))
        self.menuconsol.setTitle(cd.get_text('Консоль', key='main', id_text=8))
        self.setWindowTitle(cd.get_text('Тестирование CalcParam', key='form', id_text=1))

    def with_sound_click(self):
        cd.with_sound = self.with_sound.isChecked()
        # сразу и запомним
        if cd.with_sound:
            val = '1'
        else:
            val = 0
        cd.settings.setValue('with_sound', val)
        cd.settings.sync()

    def choice_font(self):
        font, ok = QFontDialog.getFont(self.font())
        if ok:
            self.change_font(font)

    def language_click(self):
        language = choos_language.Language(self)
        language.exec_()

    # закрыть программу
    def closeEvent(self, evt):
        self.show_rest.close()
        self.clock.need_close = True
        cd.settings.setValue("Duma", self.geometry())
        cd.settings.setValue("app_language", cd.app_lang)
        cd.settings.setValue("Font", self.font())
        cd.settings.sync()
        time.sleep(0.5)

    def change_font(self, font):
        self.setFont(font)
        # self.modeler.change_font(self.font())
        cd.settings.setValue("DumaFont", self.font())
        cd.settings.setValue("app_language", cd.app_lang)
        cd.settings.sync()
        self.set_font()

    def set_font(self):
        self.choosfont.setFont(self.font())
        self.language.setFont(self.font())
        self.with_sound.setFont(self.font())
        self.exit_action.setFont(self.font())
        self.labelTime.setFont(self.font())

    def customEvent(self, evt):
        if evt.type() == cd.StatusOperation.idType:  # изменение состояния операции
            n = evt.get_data()
            if type(n) == dict:
                pass
            else:
                if n == cd.evt_change_language:
                    self.change_language()
                    cd.send_evt(n, self.show_rest)
