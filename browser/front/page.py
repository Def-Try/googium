import pprint

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

        self.went_back = False
        self.pageselector = None
        self.browser = QWebEnginePage(self)
        self.url = None
        self.useragent = useragent
        self.active = False
        self.load_progress = 0
        self.history_ptr = [0, 0]
        self.history = [[[-1, -1]]]
        if useragent == "pc":
            self.r_useragent = BROWSER_USERAGENT_PC
        elif useragent == "mobile":
            self.r_useragent = BROWSER_USERAGENT_MOBILE
        else:
            raise ValueError("Page's useragent is invalid (not 'pc' or 'mobile')")
        self.setURL(QUrl(url))
        self.browser.profile().setHttpUserAgent(self.r_useragent)
        self.browser.profile().setPersistentStoragePath(USERDATA_PATH+"/persistent_storage")
        self.browser.loadStarted.connect(self.__loadStarted)
        self.browser.loadProgress.connect(self.__loadProgress)
        self.browser.loadFinished.connect(self.__loadFinished)
        self.browser.titleChanged.connect(self.__titleChanged)
        self.browser.iconChanged.connect(self.__iconChanged)
        self.browser.urlChanged.connect(self.__updatedURL)

    def compileHistory(self):
        pass

    def setURL(self, url: str):
        self.url = url
        self.updateURL()
        self.__updatedURL(url)

    def updateURL(self):
        self.browser.setUrl(QUrl(self.url))

    def reload(self):
        self.browser.action(QWebEnginePage.WebAction.Reload).activate(QAction.ActionEvent.Trigger)

    def back(self):
        self.went_back = True
        self.history_ptr[1] -= 1
        self.browser.action(QWebEnginePage.WebAction.Back).activate(QAction.ActionEvent.Trigger)

    def forward(self):
        self.history_ptr[1] += 1
        self.browser.action(QWebEnginePage.WebAction.Forward).activate(QAction.ActionEvent.Trigger)

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
        if not self.went_back:
            if self.history_ptr[1] < len(self.history[self.history_ptr[0]]) - 1:
                self.history += [[[self.history_ptr[0], self.history_ptr[1]]]]
                self.history_ptr[0] += 1
                self.history_ptr[1] = -1
            self.history_ptr[1] += 1
            self.history[self.history_ptr[0]].append(url)
        pprint.pprint(self.history)
        print(self.history_ptr)
        self.went_back = False
        if not self.active:
            return
        self.toolbar["urlbar"].setText(url.toString())

    def __titleChanged(self, title):
        if self.window.pagebar.currentIndex() == self.pageselector and self.active:
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
        if self.active:
            self.toolbar["progressbar"].setValue(0)
        self.load_progress = 0
        # if self.window.pagebar.currentIndex() == self.pageselector:
        #    self.window.setWindowTitle(f"{BROWSER_NAME} - Page #{self.pageselector + 1}")
        # self.window.pagebar.setTabText(self.pageselector, f"Page #{self.pageselector + 1}")

    def __loadFinished(self):
        if self.active:
            self.toolbar["progressbar"].setValue(100)
        self.load_progress = 100

    def __loadProgress(self, n):
        if self.active:
            self.toolbar["progressbar"].setValue(n)
        self.load_progress = n
