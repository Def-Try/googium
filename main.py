import sys
import os

os.chdir(os.path.dirname(__file__))

from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

from browser.back.protocol import Protocol
from browser.back.proxy import Proxy
from browser.front.browser import MainWindow

protocol, proxy = Protocol(), Proxy()
browser = QApplication(sys.argv)
protocol.preinit(QWebEngineProfile.defaultProfile())

QApplication.setApplicationName('')
window = MainWindow()
window.setMinimumSize(640, 480)
window.setMaximumSize(browser.primaryScreen().size().width(), browser.primaryScreen().size().height())
window.showMaximized()

protocol.init(browser, QWebEngineProfile.defaultProfile())
proxy.init()

browser.exec_()
