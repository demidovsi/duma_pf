from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PyQt5 import QtWidgets, QtGui

class PageControl(QWidget):

    def __init__(self, parent, orient):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout(parent)
        self.tabs = QTabWidget()
        self.tabs.setTabShape(1) # треугольничком
        self.tabs.setMovable(True) # можно переставлять
        self.tabs.setDocumentMode(True)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setTabPosition(orient)
        # self.tabs.setTabBarAutoHide(True)
        # self.tabs.setElideMode(True)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def addTab(self, NameTab):
        self.wid = QtWidgets.QWidget()
        self.tab = self.tabs.addTab(self.wid, NameTab)
        return self.wid
    def setCurrentIndex(self, index):
        self.tabs.setCurrentIndex(index)
