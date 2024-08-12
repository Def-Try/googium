from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from browser.config import *
from browser.front.page import Page


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(BROWSER_NAME)
        self.showMaximized()
        self.hide()
        self.browser = QWebEngineView(self)

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
        self.toolbar["back"].clicked.connect(lambda: self.pages[self.activePage].back())

        self.toolbar["forward"].setIcon(QIcon("assets/icons/forward.svg"))
        self.toolbar["forward"].clicked.connect(lambda: self.pages[self.activePage].forward())

        self.toolbar["refresh"].setIcon(QIcon("assets/icons/refresh.svg"))
        self.toolbar["refresh"].clicked.connect(lambda: self.pages[self.activePage].reload())

        self.toolbar["home"].setIcon(QIcon("assets/icons/home.svg"))
        self.toolbar["home"].clicked.connect(lambda: self.pages[self.activePage].home())

        self.toolbar["useragent"].setIcon(QIcon("assets/icons/useragent_pc.svg"))
        self.toolbar["useragent"].clicked.connect(lambda: self.pages[self.activePage].toggleUserAgent())

        self.toolbar["urlbar"].returnPressed.connect(
            lambda: self.pages[self.activePage].setURL(QUrl(self.toolbar["urlbar"].text()))
        )

        self.toolbar["progressbar"].setValue(100)
        self.toolbar["progressbar"].setTextVisible(False)

        self.pagebar.currentChanged.connect(self.__tab_changed)
        self.pagebar.tabCloseRequested.connect(self.__tab_closed)
        self.pagebar.addTab("New Tab")
        self.pagebar.setShape(0)
        self.pagebar.setTabsClosable(True)
        self.pagebar.setElideMode(2)

        self.layout = QVBoxLayout(self)
        self.toolbar_layout = QHBoxLayout(self)
        for k in self.toolbar:
            self.toolbar_layout.addWidget(self.toolbar[k])

        def mkpagebar():
            self.layout.addWidget(self.pagebar)

        def mktoolbar():
            self.toolbar_widget = QWidget()
            self.toolbar_widget.setLayout(self.toolbar_layout)
            self.layout.addWidget(self.toolbar_widget)
            self.toolbar_widget.adjustSize()
            self.toolbar_widget.setMaximumHeight(self.toolbar_widget.height())

        def mkbrowser():
            self.layout.addWidget(self.browser)

        if BROWSER_LAYOUT == 1:
            mkpagebar()
            mktoolbar()
            mkbrowser()
        elif BROWSER_LAYOUT == 2 or (BROWSER_LAYOUT < 1 or BROWSER_LAYOUT > 5):
            mkpagebar()
            mkbrowser()
            mktoolbar()
        elif BROWSER_LAYOUT == 3:
            mkbrowser()
            mktoolbar()
            mkpagebar()
        elif BROWSER_LAYOUT == 4:
            mkbrowser()
            mkpagebar()
            mktoolbar()
        elif BROWSER_LAYOUT == 5:
            mktoolbar()
            mkbrowser()
            mkpagebar()
        else:
            raise ValueError("Invalid layout and we haven't used a fallback. how??")

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # self.setLayout(self.layout)
        self.centralWidget.setLayout(self.layout)

    def closeEvent(self, evnt):
        for page in self.pages:
            page.compileHistory()

        super().closeEvent(evnt)

    def new_tab(self):
        page = Page(self)
        page.pageselector = self.pagebar.insertTab(
            self.pagebar.count() - 1, f"Page #{self.pagebar.count()}"
        )
        self.pages.append(page)
        return self.pagebar.count() - 2

    def __tab_changed(self, index):
        if self.pagebar.currentIndex() < len(self.pages):
            self.pages[self.pagebar.currentIndex()].active = False
        if index == self.pagebar.count() - 1:
            self.pagebar.setCurrentIndex(self.new_tab())
        self.browser.setPage(self.pages[index].browser)
        self.pages[index].active = True
        self.activePage = index
        self.toolbar['progressbar'].setValue(self.pages[index].load_progress)
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
        self.pages.pop(index).deleteLater()
        self.pagebar.removeTab(index)
