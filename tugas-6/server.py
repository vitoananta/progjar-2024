from socket import *
import socket
import threading
import json
import logging
import time
from chat import Chat

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
                    try:
                        message = json.loads(rcv.strip())
                        if 'command' in message and message['command'] == 'crossrealm_send':
                            hasil = json.dumps(self.chatserver.send_message_cross_realm(message))
                        else:
                            hasil = json.dumps(self.chatserver.proses(rcv))
                    except json.JSONDecodeError:
                        hasil = json.dumps(self.chatserver.proses(rcv))
                    hasil = hasil + "\r\n\r\n"
                    logging.warning("balas ke client: {}".format(hasil))
                    self.connection.sendall(hasil.encode())
                    rcv = ""
            else:
                break
        self.connection.close()


class Server(threading.Thread):
    def __init__(self, host, port, target_host, target_port):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.target_host = target_host
        self.target_port = target_port
        self.realm_connector = RealmConnector(host, port, target_host, target_port)
        self.chatserver = Chat(self.realm_connector)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind((self.host, self.port))
        self.my_socket.listen(1)
        self.realm_connector.start()
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning("connection from {}".format(self.client_address))
            
            clt = ProcessTheClient(self.connection, self.client_address, self.chatserver)
            clt.start()
            self.the_clients.append(clt)

class RealmConnector(threading.Thread):
    _instance = None

    @staticmethod
    def get_instance():
        return RealmConnector._instance

    def __init__(self, host, port, target_host, target_port):
        RealmConnector._instance = self
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

    def send_cross_realm_message(self, username_from, username_dest, message):
        try:
            if not self.connection:
                return {'status': 'ERROR', 'message': 'No connection to target realm'}
            message = json.dumps({
                'command': 'crossrealm_send',
                'username_from': username_from,
                'username_dest': username_dest,
                'message': message
            }) + "\r\n"
            self.connection.sendall(message.encode())
            return {'status': 'OK', 'message': 'Message sent to other realm'}
        except Exception as e:
            logging.error(f"Failed to send message to other realm: {e}")
            return {'status': 'ERROR', 'message': 'Failed to send message to other realm'}


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
    svr = Server(host, port, target_host, target_port)
    svr.start()

if __name__ == "__main__":
    main()
