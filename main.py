import sys
import os

from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

from browser.back.protocol import Protocol
from browser.back.proxy import Proxy
from browser.front.browser import MainWindow
from browser.config import *

os.chdir(os.path.dirname(__file__))

protocol, proxy = Protocol(), None
if PROXY_ACTIVE:
    proxy = Proxy()
browser = QApplication(sys.argv)
protocol.preinit()

QApplication.setApplicationName('')
window = MainWindow()
window.setMinimumSize(640, 480)
window.setMaximumSize(browser.primaryScreen().size().width(), browser.primaryScreen().size().height())
window.showMaximized()

protocol.init(browser, QWebEngineProfile.defaultProfile())
if PROXY_ACTIVE:
    proxy.init()

browser.exec_()
