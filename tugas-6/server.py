from socket import *
import socket
import threading
import json
import logging
import time
from chat import Chat

chatserver = Chat()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        rcv = ""
        while True:
            data = self.connection.recv(512)
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv[-2:] == '\r\n':
                    # end of command, process string
                    logging.warning("data dari client: {}".format(rcv))
                    hasil = json.dumps(chatserver.proses(rcv))
                    hasil = hasil + "\r\n\r\n"
                    logging.warning("balas ke  client: {}".format(hasil))
                    self.connection.sendall(hasil.encode())
                    rcv = ""
            else:
                break
        self.connection.close()

class Server(threading.Thread):
    def __init__(self, host, port):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind((self.host, self.port))
        self.my_socket.listen(1)
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning("connection from {}".format(self.client_address))
            
            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()
            self.the_clients.append(clt)

class RealmConnector(threading.Thread):
    def __init__(self, host, port, target_host, target_port):
        self.host = host
        self.port = port
        self.target_host = target_host
        self.target_port = target_port
        self.connection = None
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((self.target_host, self.target_port))
                logging.warning("Connected to target realm at {}:{}".format(self.target_host, self.target_port))
                return  # Exit the thread once connected
            except Exception as e:
                logging.warning("Failed to connect to target realm: {}. Retrying...".format(e))
                self.connection.close()
                self.connection = None
                time.sleep(5)

def main():
    realm = input("Pilih salah satu realm (alpha/beta):")
    host = "0.0.0.0"
    if realm == "alpha":
        port = 9993
        target_host = "localhost"
        target_port = 8889
    elif realm == "beta":
        port = 8889
        target_host = "localhost"
        target_port = 9993
    else:
        print("Realm tidak ditemukan")
        return

    print("Server berjalan pada {} port {}".format(host, port))
    svr = Server(host, port)
    svr.start()

    while True:
        cmd = input("Type 'connect' to try to connect to the other realm: ")
        if cmd == "connect":
            connector = RealmConnector(host, port, target_host, target_port)
            connector.start()

if __name__ == "__main__":
    main()
