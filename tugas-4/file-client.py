import socket
import json
import base64
import logging
import os

server_address = ('0.0.0.0', 7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall((command_str + "\r\n\r\n").encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False

def remote_list():
    command_str = f"LIST"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    if not filename:
        print("Gagal: file yang ingin diambil kosong")
        return False
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        nama_file = hasil['data_namafile']
        isi_file = base64.b64decode(hasil['data_file'])
        with open(nama_file, 'wb') as fp:
            fp.write(isi_file)
        print(f"Berhasil: {filename} {hasil['data_pesan']}")
        return True
    else:
        print(f"Gagal: {hasil['data']}")
        return False

def remote_upload(filename=""):
    if not filename:
        print("Gagal: file yang ingin diupload kosong")
        return False
    if not os.path.exists(filename):
        print("Gagal: file yang ingin diupload tidak ada")
        return False
    try:
        with open(filename, 'rb') as file:
            file_content = file.read()
            file_content_base64 = base64.b64encode(file_content).decode('utf-8')
            command_str = f"UPLOAD {filename} {file_content_base64}"
            hasil = send_command(command_str)
            if hasil and hasil['status'] == 'OK':
                print(f"Berhasil: {filename} {hasil['data_pesan']}")
                return True
            else:
                print(f"Gagal: {hasil['data']}")
                return False
    except Exception as e:
        print(f"Gagal: {str(e)}")
        return False

def remote_delete(filename=""):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print(f"Berhasil: {filename} {hasil['data_pesan']}")
        return True
    else:
        print(f"Gagal: {hasil['data']}")
        return False

if __name__ == '__main__':
    server_address = ('172.16.16.101', 10946)
    #contoh pemakaian
    # remote_list()
    # remote_get('donalbebek.jpg')
    # remote_get('')
    # remote_get('gagal-get.txt')
    # remote_upload('boris.jpg')
    # remote_upload('musuh-donal-bebek.txt')
    # remote_upload('')
    # remote_upload('gagal-upload.png')
    # remote_delete('musuh-donal-bebek.txt')
    # remote_delete('')
    # remote_delete('gagal-hapus.png')
    

