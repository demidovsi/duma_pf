import sys
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, QtGui, QtCore
import commondata
import form
import time

app = QtWidgets.QApplication(sys.argv)
app.setFont(QtGui.QFont('Arial', 9))
# app.setStyle("Fusion")

commondata.settings = QtCore.QSettings("Демидов", "Дума РФ")
if commondata.settings.contains("app_language"):
    commondata.app_lang = commondata.settings.value("app_language", "ru")
commondata.load_texts(commondata.app_lang)

splash = QtWidgets.QSplashScreen(QtGui.QPixmap("Безымянный.jpg"))
splash.showMessage('Инициация программы "Дума РФ"', QtCore.Qt.AlignTop, QtCore.Qt.white)
splash.show()
time.sleep(1)

win = form.Form()
win.setWindowIcon(QIcon('icons/CalcParam.ico'))
win.show()

splash.finish(win)
# Run the program
sys.exit(app.exec())
