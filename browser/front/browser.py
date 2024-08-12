from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

from browser.config import *
from browser.front.page import Page


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(BROWSER_NAME)
        self.showMaximized()
        self.hide()

        self.pages = []
        self.activePage = 0

        self.pagebar = QTabBar(self)

        self.toolbar = {
            "back": QPushButton("Back"),
            "forward": QPushButton("Forward"),
            "refresh": QPushButton("Refresh"),
            "home": QPushButton("Home"),
            "useragent": QPushButton("PC"),
            "urlbar": QLineEdit(self),
            "progressbar": QProgressBar(self),
        }
        self.toolbar["back"].setIcon(QIcon("assets/icons/back.svg"))
        self.toolbar["back"].clicked.connect(lambda: self.browser.back())

        self.toolbar["forward"].setIcon(QIcon("assets/icons/forward.svg"))
        self.toolbar["forward"].clicked.connect(lambda: self.browser.forward())

        self.toolbar["refresh"].setIcon(QIcon("assets/icons/refresh.svg"))
        self.toolbar["refresh"].clicked.connect(lambda: self.browser.reload())

        self.toolbar["home"].setIcon(QIcon("assets/icons/home.svg"))
        self.toolbar["home"].clicked.connect(lambda: self.pages[self.activePage].home())

        self.toolbar["useragent"].setIcon(QIcon("assets/icons/useragent_pc.svg"))
        self.toolbar["useragent"].clicked.connect(
            lambda: self.pages[self.activePage].toggleUserAgent()
        )

        self.toolbar["urlbar"].returnPressed.connect(
            lambda: self.pages[self.activePage].setURL(self.toolbar["urlbar"].text())
        )

        self.toolbar["progressbar"].setValue(100)
        self.toolbar["progressbar"].setTextVisible(False)

        self.pagebar.currentChanged.connect(self.__tab_changed)
        self.pagebar.tabCloseRequested.connect(self.__tab_closed)
        self.pagebar.addTab(QWidget(), "New Tab")
        self.pagebar.setTabsClosable(True)
        self.pagebar.setTabShape(1)
        self.pagebar.setElideMode(2)

        self.setCentralWidget(self.pagebar)

    def new_tab(self):
        page = Page(self)
        page.pageselector = self.pagebar.insertTab(
            self.pagebar.count() - 1, page, f"Page #{self.pagebar.count()}"
        )
        return self.pagebar.count() - 2

    def __tab_changed(self, index):
        if index == self.pagebar.count() - 1:
            self.pagebar.setCurrentIndex(self.new_tab())
        self.setWindowTitle(f"{BROWSER_NAME} - {self.pagebar.tabText(index)}")

    def __tab_closed(self, index):
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
