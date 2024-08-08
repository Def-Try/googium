from PyQt5.QtNetwork import QNetworkProxy

import socket, sys
from _thread import start_new_thread
from urllib.parse import urlparse
import random

BUFFER_SIZE = 1024 * 64


class ProxyRunner:
    # Constructors initializing basic architecture
    def __init__(self, host='127.0.0.1', port=6913):
        self.host = host
        self.port = port

    def start_server(self, conn=5):
        try:
            self.listen(conn)
        except Exception as e:
            print("Terminating proxy server!")
            print(e)
        finally:
            sys.exit()

    # Listener for incoming connections
    def listen(self, max_conns):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self.host, self.port))
            s.listen(max_conns)
            print("Proxy server listening...")
        except Exception as e:
            print("Could not start up")
            raise e

        while True:
            try:
                conn, addr = s.accept()
                start_new_thread(self.handle_connection, (conn,))
            except Exception as e:
                print("Could not establish a connection")
                raise e

    def handle_connection(self, conn):
        request = conn.recv(BUFFER_SIZE).decode()
        beginning = request.split('\r\n')[0]
        headers = ('\r\n'.join(request.split('\r\n')[1:]).split('\r\n\r\n')[0]).split('\r\n')
        headers = {i.split(":")[0].strip().lower(): i.split(":")[1].strip() for i in headers}
        del headers['proxy-connection']
        data = '\r\n\r\n'.join('\r\n'.join(request.split('\r\n')[1:]).split('\r\n\r\n')[1:])
        method, *host, version = beginning.split(" ")
        host = " ".join(host).strip()
        if method == "GET":
            self.method_http(conn, method, host, headers, data)
        elif method == "CONNECT":
            # CONNECT often raises random errors when connection is closed from either side.
            # We don't care about it, so let's ignore
            try:
                self.method_https(conn, method, host, headers, data)
            except Exception:
                pass
        return conn.close()

    @staticmethod
    def method_http(conn, method, uri, headers, data):
        request = (f"{method}  {uri} HTTP/1.1\r\nConnection: close\r\n"
                   f"{'\r\n'.join(''.join(random.choice((str.upper,str.lower))(x) for x in k) + ':' + v for k, v in headers.items())}\r\n\r\n"
                   f"{data}").encode()
        # F*ck active DPI:
        #     1. add additional space between method and URI
        #     2. Randomize case for header names
        uriparsed = urlparse(uri)
        if uriparsed.scheme != 'http':
            raise ValueError("attempted to request GET from non-HTTP protocol?")
        host = uriparsed.netloc.split(':')[0]
        port = int(uriparsed.netloc.split(':')[1]) if ':' in uriparsed.netloc else 80

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(request)
        while s.fileno() != -1:
            d = s.recv(BUFFER_SIZE)
            if d == b'':
                break
            conn.send(d)
        return

    @staticmethod
    def method_https(conn, method, uri, headers, data):
        uriparsed = urlparse("h://" + uri)
        host = uriparsed.netloc.split(':')[0]
        port = int(uriparsed.netloc.split(':')[1]) if ':' in uriparsed.netloc else 80

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        conn.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

        conn.settimeout(1)
        s.settimeout(1)

        while s.fileno() != -1:
            try:
                d = conn.recv(BUFFER_SIZE)
            except TimeoutError:
                break
            while d != b'':
                s.send(d)
                try:
                    d = conn.recv(BUFFER_SIZE)
                except TimeoutError:
                    break
            try:
                d = s.recv(BUFFER_SIZE)
            except TimeoutError:
                break
            while d != b'':
                conn.send(d)
                try:
                    d = s.recv(BUFFER_SIZE)
                except TimeoutError:
                    break


class Proxy(QNetworkProxy):
    def __init__(self):
        super().__init__()
        self.setType(QNetworkProxy.HttpProxy)
        self.setHostName("127.0.0.1")
        self.setPort(6913)

    def init(self):
        QNetworkProxy.setApplicationProxy(self)
        server = ProxyRunner()
        start_new_thread(server.start_server, tuple())
