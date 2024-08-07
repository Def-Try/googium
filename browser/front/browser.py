import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from browser.config import *
from .page import Page

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(BROWSER_NAME)
        self.showMaximized()
        self.hide()

        self.pages = []
        self.activePage = 0

        self.pagebar = QTabWidget(self)
        self.pagebar.currentChanged.connect(self.__tabChanged)
        self.pagebar.tabCloseRequested.connect(self.__tabClosed)
        self.pagebar.addTab(QWidget(), "New Tab")
        self.pagebar.setTabsClosable(True)
        self.pagebar.setTabShape(1)
        self.pagebar.setElideMode(2)

        self.setCentralWidget(self.pagebar)

    def newTab(self):
        page = Page(self)
        page.pageselector = self.pagebar.insertTab(self.pagebar.count() - 1, page, f'Page #{self.pagebar.count()}')
        return self.pagebar.count() - 2

    def __tabChanged(self, index):
        if index == self.pagebar.count() - 1:
            self.pagebar.setCurrentIndex(self.newTab())
        self.setWindowTitle(f"{BROWSER_NAME} - {self.pagebar.tabText(index)}")

    def __tabClosed(self, index):
        if index == self.pagebar.count() - 1:
            return
        if self.pagebar.currentIndex() == index:
            if self.pagebar.currentIndex() == 0:
                if self.pagebar.count() == 2:
                    return self.close()
                self.pagebar.setCurrentIndex(1)
            else:
                self.pagebar.setCurrentIndex(self.pagebar.currentIndex() - 1)
        self.pagebar.widget(index).deleteLater()
        self.pagebar.removeTab(index)