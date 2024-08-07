from PyQt5.QtCore import QObject, QBuffer, QIODevice
from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlScheme
import mimetypes

class GOOGScheme(QWebEngineUrlSchemeHandler):
	scheme: str = b"goog"

	def __init__(self, app):
		super().__init__(app)

	def requestStarted(self, request):
		url = request.requestUrl()
		requested = url.toString()[len(self.scheme)+3:]

		data = b'ERR'
		type_ = b'text/text'

		if requested == 'home':
			requested = 'asset/html/home.html'
		if requested.startswith('asset/'):
			try:
				with open(f'assets/{requested[6:]}', 'rb') as file:
					data = file.read()
			except: pass
			type_ = (mimetypes.guess_type(f'assets/{requested[6:]}')[0] or 'application/octet-stream').encode()

		buf = QBuffer(parent=self)
		request.destroyed.connect(buf.deleteLater)
		buf.open(QIODevice.WriteOnly)
		buf.write(data)
		buf.seek(0)
		buf.close()
		request.reply(type_, buf)
		return

class Protocol:
	@staticmethod
	def preinit(profile):
		QWebEngineUrlScheme.registerScheme(QWebEngineUrlScheme(GOOGScheme.scheme))
	def init(self, app, profile):
		self.handle = GOOGScheme(app)
		profile.installUrlSchemeHandler(GOOGScheme.scheme, self.handle)
