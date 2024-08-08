import random
import socket
import sys
from _thread import start_new_thread
from urllib.parse import urlparse

from PyQt5.QtNetwork import QNetworkProxy

from browser.config import *


def get_chokes(data, minchoke, maxchoke):
    chokes, ptr = [], 0
    while ptr < len(data):
        leng = random.randrange(minchoke, maxchoke)
        chokes.append(data[ptr:min(len(data), ptr+leng)])
        ptr += leng
    return chokes


class ProxyRunner:
    # Constructors initializing basic architecture
    def __init__(self, host='127.0.0.1', port=6913):
        self.host = host
        self.port = port

    def start_server(self, conn):
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
        request = conn.recv(PROXY_BUFFER_SIZE).decode()
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
            try:
                self.method_https(conn, method, host, headers, data)
            except ConnectionAbortedError:
                pass
            except ConnectionResetError:
                pass
        return conn.close()

    @staticmethod
    def method_http(conn, method, uri, headers, data):
        request = f"{method}  {uri} HTTP/1.1\r\nConnection: close\r\n"
        for k, v in headers.items():
            request += ''.join(random.choice((str.upper, str.lower))(x) for x in k) + ":" + v
            request += "\r\n"
        request += "\r\n"
        request += data
        request = request.encode()
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

        for choke in get_chokes(request, 2, 16):
            s.sendall(choke)
        # F*ck active DPI:
        #     Fragmentation of data, making DPI "choke" on small packets of data
        while s.fileno() != -1:
            d = s.recv(PROXY_BUFFER_SIZE)
            if d == b'':
                break
            conn.sendall(d)
        return

    @staticmethod
    def method_https(conn, _1, uri, _2, _3):
        uriparsed = urlparse("h://" + uri)
        host = uriparsed.netloc.split(':')[0]
        port = int(uriparsed.netloc.split(':')[1]) if ':' in uriparsed.netloc else 80

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        conn.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

        conn.settimeout(1)
        s.settimeout(1)

        sent_packets = 0
        while s.fileno() != -1:
            sent_packets += 1
            try:
                d = conn.recv(PROXY_BUFFER_SIZE)
            except TimeoutError:
                pass
            while d != b'':
                if sent_packets < 12:
                    # HTTPS handshake isn't completed, choke our connection until all data is encrypted
                    for choke in get_chokes(d, 128, 512):
                        s.sendall(choke)
                    # F*ck active DPI:
                    #     Fragmentation of data, making DPI "choke" on small packets of data
                else:
                    # HTTPS handshake was probable completed, let's not limit our connection now
                    s.sendall(d)
                try:
                    d = conn.recv(PROXY_BUFFER_SIZE)
                except TimeoutError:
                    break
            try:
                d = s.recv(PROXY_BUFFER_SIZE)
            except TimeoutError:
                pass
            while d != b'':
                conn.sendall(d)
                try:
                    d = s.recv(PROXY_BUFFER_SIZE)
                except TimeoutError:
                    break


class Proxy(QNetworkProxy):
    def __init__(self):
        super().__init__()
        self.setType(QNetworkProxy.HttpProxy)
        self.setHostName(PROXY_LISTEN_HOST)
        self.setPort(PROXY_LISTEN_PORT)

    def init(self):
        QNetworkProxy.setApplicationProxy(self)
        server = ProxyRunner(PROXY_LISTEN_HOST, PROXY_LISTEN_PORT)
        start_new_thread(server.start_server, (10,))
