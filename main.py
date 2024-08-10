import os
import sys

from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

from browser.back.protocol import Protocol
from browser.back.proxy import Proxy
from browser.config import *
from browser.front.browser import MainWindow

protocol, proxy = Protocol(), None
if PROXY_ACTIVE:
    proxy = Proxy()
browser = QApplication(sys.argv)
protocol.preinit()

QApplication.setApplicationName("")
window = MainWindow()
window.setMinimumSize(640, 480)
window.setMaximumSize(
    browser.primaryScreen().size().width(), browser.primaryScreen().size().height()
)
window.showMaximized()

protocol.init(browser, QWebEngineProfile.defaultProfile())
if PROXY_ACTIVE:
    proxy.init()

browser.exec_()
