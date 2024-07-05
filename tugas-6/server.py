from socket import *
import socket
import threading
import json
import logging
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

def main():
    realm = input("Pilih salah satu realm (alpha/beta):")
    host = "0.0.0.0"
    if realm == "alpha":
        port = 9993
    elif realm == "beta":
        port = 8889
    else:
        print("Realm tidak ditemukan")
        return
    print("Server berjalan pada {} port {}".format(host, port))
    svr = Server(host, port)
    svr.start()

if __name__ == "__main__":
    main()