from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

from browser.config import *


class Page(QWidget):
    def __init__(self, window, url: str = BROWSER_HOME, useragent: str = "pc"):
        super().__init__()

        self.window = window
        self.toolbar = window.toolbar

        self.pageselector = None
        self.browser = QWebEnginePage(self)
        self.url = None
        self.useragent = useragent
        if useragent == "pc":
            self.r_useragent = BROWSER_USERAGENT_PC
        elif useragent == "mobile":
            self.r_useragent = BROWSER_USERAGENT_MOBILE
        else:
            raise ValueError("Page's useragent is invalid (not 'pc' or 'mobile')")
        self.setURL(QUrl(url))
        self.browser.profile().setHttpUserAgent(self.r_useragent)
        self.browser.loadStarted.connect(self.__loadStarted)
        self.browser.loadProgress.connect(self.__loadProgress)
        self.browser.loadFinished.connect(self.__loadFinished)
        self.browser.titleChanged.connect(self.__titleChanged)
        self.browser.iconChanged.connect(self.__iconChanged)
        self.browser.urlChanged.connect(self.__updatedURL)

    def setURL(self, url: str):
        self.url = url
        self.updateURL()
        self.__updatedURL(url)

    def updateURL(self):
        self.browser.setUrl(QUrl(self.url))

    def refresh(self):
        self.browser.reload()

    def back(self):
        self.browser.back()

    def forward(self):
        self.browser.forward()

    def home(self):
        self.setURL(BROWSER_HOME)

    def toggleUserAgent(self):
        if self.useragent == "pc":
            self.r_useragent = BROWSER_USERAGENT_MOBILE
            self.useragent = "mobile"
        elif self.useragent == "mobile":
            self.r_useragent = BROWSER_USERAGENT_PC
            self.useragent = "pc"
        else:
            raise ValueError("Page's useragent is invalid (not 'pc' or 'mobile')")
        self.browser.page().profile().setHttpUserAgent(self.r_useragent)
        self.browser.stop()
        if self.useragent == "pc":
            self.browser.resize(
                self.browser.parent().frameGeometry().width(),
                self.browser.parent().frameGeometry().height(),
            )
            self.browser.setMaximumSize(16777215, 16777215)
            self.browser.move(0, 0)
        elif self.useragent == "mobile":
            self.browser.resize(
                int(self.browser.parent().frameGeometry().height() * 9 / 16),
                self.browser.parent().frameGeometry().height(),
            )
            self.browser.setMaximumSize(
                int(self.browser.parent().frameGeometry().height() * 9 / 16),
                self.browser.parent().frameGeometry().height(),
            )
            self.browser.move(
                int(
                    self.browser.parent().frameGeometry().width() / 2
                    - self.browser.frameGeometry().width() / 2
                ),
                0,
            )
        self.browser.reload()
        self.toolbar["useragent"].setText("PC" if self.useragent == "pc" else "Mobile")
        self.toolbar["useragent"].setIcon(
            QIcon(
                "assets/icons/useragent_pc.svg"
                if self.useragent == "pc"
                else "assets/icons/useragent_mobile.svg"
            )
        )

    def __updatedURL(self, url):
        self.toolbar["urlbar"].setText(url.toString())

    def __titleChanged(self, title):
        if self.window.pagebar.currentIndex() == self.pageselector:
            self.window.setWindowTitle(f"{BROWSER_NAME} - {title}")
        title = (
            title
            if len(title) < TAB_TITLE_CUTOFF
            else title[: TAB_TITLE_CUTOFF - 3] + "..."
        )
        self.window.pagebar.setTabText(self.pageselector, title)

    def __iconChanged(self, icon):
        self.window.pagebar.setTabIcon(self.pageselector, icon)

    def __loadStarted(self):
        self.toolbar["progressbar"].setValue(0)
        # if self.window.pagebar.currentIndex() == self.pageselector:
        #    self.window.setWindowTitle(f"{BROWSER_NAME} - Page #{self.pageselector + 1}")
        # self.window.pagebar.setTabText(self.pageselector, f"Page #{self.pageselector + 1}")

    def __loadFinished(self):
        self.toolbar["progressbar"].setValue(100)

    def __loadProgress(self, n):
        self.toolbar["progressbar"].setValue(n)
