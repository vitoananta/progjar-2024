from socket import *
import socket
import threading
import json
import logging
from chat import Chat, RealmThreadCommunication

chatserver_alpha = Chat()
chatserver_beta = Chat()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address, chatserver):
        self.connection = connection
        self.address = address
        self.chatserver = chatserver
        threading.Thread.__init__(self)

    def run(self):
        rcv = ""
        while True:
            data = self.connection.recv(512)
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv[-2:] == '\r\n':
                    logging.warning("data dari client: {}".format(rcv))
                    hasil = json.dumps(self.chatserver.proses(rcv))
                    hasil = hasil + "\r\n\r\n"
                    logging.warning("balas ke  client: {}".format(hasil))
                    self.connection.sendall(hasil.encode())
                    rcv = ""
            else:
                break
        self.connection.close()

class Server(threading.Thread):
    def __init__(self, host, port, chatserver):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.chatserver = chatserver
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind((self.host, self.port))
        self.my_socket.listen(1)
        logging.warning("Server berjalan pada {} port {}".format(self.host, self.port))
        
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning("connection from {}".format(self.client_address))
            
            clt = ProcessTheClient(self.connection, self.client_address, self.chatserver)
            clt.start()
            self.the_clients.append(clt)

class RealmConnection(threading.Thread):
    def __init__(self, chatserver, dest_address, dest_port):
        threading.Thread.__init__(self)
        self.chatserver = chatserver
        self.dest_address = dest_address
        self.dest_port = dest_port

    def run(self):
        rtc = RealmThreadCommunication(self.chatserver, self.dest_address, self.dest_port)
        self.chatserver.realm_communication_threads.append(rtc)
        rtc.start()

def main():
    host = "0.0.0.0"
    alpha_port = 8889
    beta_port = 8890
    alpha_dest_address = "127.0.0.1"
    beta_dest_address = "127.0.0.1"

    realmAlpha = Server(host, alpha_port, chatserver_alpha)
    realmBeta = Server(host, beta_port, chatserver_beta)
    realmAlpha.start()
    realmBeta.start()

    # Establish connection between realms
    alpha_to_beta = RealmConnection(chatserver_alpha, beta_dest_address, beta_port)
    beta_to_alpha = RealmConnection(chatserver_beta, alpha_dest_address, alpha_port)
    alpha_to_beta.start()
    beta_to_alpha.start()

if __name__ == "__main__":
    main()
