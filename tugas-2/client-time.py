import socket
import logging

def send_time_request(sock):
    message = 'TIME\r\n'
    logging.warning(f"Sending from CLIENT: {message}")
    sock.sendall(message.encode('utf-8'))

    data = sock.recv(32)
    logging.warning(f"Received from SERVER: {data.decode('utf-8')}")

def send_quit_request(sock):
    message = 'QUIT\r\n'
    logging.warning(f"Sending from CLIENT: {message}")
    sock.sendall(message.encode('utf-8'))

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('172.16.16.101', 45000)
    logging.warning(f"Connecting to {server_address}")
    sock.connect(server_address)

    try:
        send_time_request(sock)
        send_quit_request(sock)
    finally:
        logging.warning("Closing")
        sock.close()

if __name__=='__main__':
    main()
