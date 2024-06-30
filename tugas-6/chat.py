import json
import uuid
import logging
from queue import  Queue
import threading 
import socket

class RealmThreadCommunication(threading.Thread):
    def __init__(self, chats, realm_dest_address, realm_dest_port):
        self.chats = chats
        self.chat = {}
        self.realm_dest_address = realm_dest_address
        self.realm_dest_port = realm_dest_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.realm_dest_address, self.realm_dest_port))
        threading.Thread.__init__(self)

    def send_string(self, string):
        try:
            self.sock.sendall(string.encode())
            recv_msg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server", data)
                if data:
                    recv_msg = "{}{}".format(recv_msg, data.decode())
                    if recv_msg[-4:] == '\r\n\r\n':
                        print("end of string")
                        return json.loads(recv_msg)
        except:
            self.sock.close()
            return {'status': 'ERROR', 'message': 'Gagal'}

    def put(self, message):
        dest = message["msg_to"]
        try:
            self.chat[dest].put(message)
        except KeyError:
            self.chat[dest] = Queue()
            self.chat[dest].put(message)


class Chat:
    def __init__(self):
        self.sessions={}
        self.users = {}
        self.group = {}
        self.users['messi']={ 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {}}
        self.users['henderson']={ 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
        self.users['lineker']={ 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}}
        self.realms = {}

    def proses(self,data):
        j=data.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                logging.warning("AUTH: auth {} {}" . format(username,password))
                return self.autentikasi_user(username,password)
            
            elif (command=='register'):
                username=j[1].strip()
                password=j[2].strip()
                nama=j[3].strip()
                negara=j[4].strip()
                logging.warning("REGISTER: register {} {}" . format(username,password))
                return self.register_user(username,password, nama, negara)

            elif command == "logout":
                return self.logout()
            
            elif (command=='send'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message=""
                for w in j[3:]:
                    message="{} {}" . format(message,w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
                return self.send_message(sessionid,usernamefrom,usernameto,message)
            
            elif (command=='inbox'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOX: {}" . format(sessionid))
                return self.get_inbox(username)
            
            elif (command=='creategroup'):
                sessionid = j[1].strip()
                groupname = j[2].strip()
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("CREATEGROUP: session {} added group {}" . format(sessionid, groupname))
                return self.create_group(sessionid,usernamefrom,groupname)
            
            elif (command == 'joingroup'):
                sessionid = j[1].strip()
                groupname = j[2].strip()
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("JOINGROUP: session {} added group {}" . format(sessionid, groupname))
                return self.join_group(sessionid, usernamefrom, groupname)
            
            elif command == 'joingrouprealm':
                sessionid = j[1].strip()
                realm_id = j[2].strip()
                groupname = j[3].strip()
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("JOINGROUPREALM: session {} trying to join group {} in realm {}".format(sessionid, groupname, realm_id))
                return self.join_group_realm(sessionid, realm_id, usernamefrom, groupname)
          
            elif command == "addrealm":
                realm_id = j[1].strip()
                realm_dest_address = j[2].strip()
                realm_dest_port = int(j[3].strip())
                logging.warning("ADDREALM: realm {} on {} port {}" . format(realm_id, realm_dest_address, realm_dest_port))
                return self.add_realm(realm_id, realm_dest_address, realm_dest_port, data)

            elif command == "sendrealm":
                sessionid = j[1].strip()
                realm_id = j[2].strip()
                usernameto = j[3].strip()
                message = ""
                for w in j[4:]:
                    message = "{} {}".format(message, w)
                print(message)
                usernamefrom = self.sessions[sessionid]["username"]
                logging.warning(
                    "SENDREALM: session {} send message from {} to {} in realm {}".format(
                        sessionid, usernamefrom, usernameto, realm_id
                    )
                )
                return self.send_realm_message(sessionid, realm_id, usernamefrom, usernameto, message, data)
            
            elif command == "recvrealm":
                realm_id = j[1].strip()
                realm_dest_address = j[2].strip()
                realm_dest_port = int(j[3].strip())
                return self.recv_realm(realm_id, realm_dest_address, realm_dest_port, data)
            
            elif command == "recvprivaterealm":
                usernamefrom = j[1].strip()
                realm_id = j[2].strip()
                usernameto = j[3].strip()
                message = ""
                for w in j[4:]:
                    message = "{} {}".format(message, w)
                print(message)
                logging.warning(
                    "RECVPRIVATEREALMMSG: recieve message from {} to {} in realm {}".format(
                        usernamefrom, usernameto, realm_id
                    )
                )
                return self.recv_private_realm_message(realm_id, usernamefrom, usernameto, message, data)
            
            elif command == "recvjoingrouprealm":
                usernamefrom = j[1].strip()
                groupname = j[2].strip()
                return self.recv_join_group_realm(usernamefrom, groupname)
            
            elif command == "listmembers":
                sessionid = j[1].strip()
                groupname = j[2].strip()
                logging.warning("LISTMEMBERS: session {} for group {}".format(sessionid, groupname))
                return self.list_group_members(sessionid, groupname)
            
            else:
                logging.warning(command)
                return {"status": "ERROR", "message": "**Protocol Tidak Benar"}
        except KeyError:
            return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
        except IndexError:
            return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}

    def autentikasi_user(self,username,password):
        if (username not in self.users):
            return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
        if (self.users[username]['password']!= password):
            return { 'status': 'ERROR', 'message': 'Password Salah' }
        tokenid = str(uuid.uuid4()) 
        self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
        return { 'status': 'OK', 'tokenid': tokenid }
    
    def register_user(self,username, password, nama, negara):
        if (username in self.users):
            return { 'status': 'ERROR', 'message': 'User Sudah Ada' }
        nama = nama.replace("_", " ")
        self.users[username]={ 
            'nama': nama,
            'negara': negara,
            'password': password,
            'incoming': {},
            'outgoing': {}
            }
        tokenid = str(uuid.uuid4()) 
        self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
        return { 'status': 'OK', 'tokenid': tokenid }
    
    def logout(self, sessionid):
        if (bool(self.sessions) == True):
            del self.sessions[sessionid]
            return {'status': 'OK'}
        else:
            return {'status': 'ERROR', 'message': 'Belum Login'}

    def get_user(self,username):
        if (username not in self.users):
            return False
        return self.users[username]
    
    def send_message(self,sessionid,username_from,username_dest,message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)

        if (s_fr==False or s_to==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:	
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from]=Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from]=Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}
    
    def get_inbox(self,username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs={}
        for users in incoming:
            msgs[users]=[]
            while not incoming[users].empty():
                msgs[users].append(s_fr['incoming'][users].get_nowait())
        return {'status': 'OK', 'messages': msgs}
    
    def get_group(self, group_name):
        if (group_name not in self.group):
            return False
        return self.group[group_name]

    def create_group(self, sessionid, usernamefrom, groupname):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        self.group[groupname] = {
            'admin': usernamefrom,
            'members': [{'username': usernamefrom, 'realm': 'local'}],  # Local realm for the group creator
            'message': {}
        }
        return {'status': 'OK', 'message': 'Add group successful'}
    
    def join_group(self, sessionid, usernamefrom, groupname):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if usernamefrom in [member['username'] for member in self.group[groupname]['members']]:
            return {'status': 'ERROR', 'message': 'User sudah dalam group'}
        self.group[groupname]['members'].append({'username': usernamefrom, 'realm': 'local'})
        return {'status': 'OK', 'message': 'Join group successful'}
    
    def join_group_realm(self, sessionid, realm_id, usernamefrom, groupname):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if realm_id not in self.realms:
            return {'status': 'ERROR', 'message': 'Realm Tidak Ditemukan'}
        
        j = f"recvjoingrouprealm {usernamefrom} {groupname}\r\n"
        result = self.realms[realm_id].send_string(j)
        
        # If successful, add the user to the group with the realm information
        if result['status'] == 'OK':
            if groupname not in self.group:
                self.group[groupname] = {
                    'admin': usernamefrom,
                    'members': [],
                    'message': {}
                }
            self.group[groupname]['members'].append({'username': usernamefrom, 'realm': realm_id})
        
        return result
    
    def add_realm(self, realm_id, realm_dest_address, realm_dest_port, data):
        j = data.split()
        j[0] = "recvrealm"
        data = " ".join(j)
        data += "\r\n"
        if realm_id in self.realms:
            return {"status": "ERROR", "message": "Realm sudah ada"}

        self.realms[realm_id] = RealmThreadCommunication(
            self, realm_dest_address, realm_dest_port
        )
        result = self.realms[realm_id].send_string(data)
        return result

    def send_realm_message(
        self, sessionid, realm_id, username_from, username_dest, message, data
    ):
        if sessionid not in self.sessions:
            return {"status": "ERROR", "message": "Session Tidak Ditemukan"}
        if realm_id not in self.realms:
            return {"status": "ERROR", "message": "Realm Tidak Ditemukan"}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)
        if s_fr == False or s_to == False:
            return {"status": "ERROR", "message": "User Tidak Ditemukan"}
        message = {"msg_from": s_fr["nama"], "msg_to": s_to["nama"], "msg": message}
        self.realms[realm_id].put(message)

        j = data.split()
        j[0] = "recvprivaterealm"
        j[1] = username_from
        data = " ".join(j)
        data += "\r\n"
        self.realms[realm_id].send_string(data)
        return {"status": "OK", "message": "Message Sent to Realm"}

    
    def recv_realm(self, realm_id, realm_dest_address, realm_dest_port, data):
        self.realms[realm_id] = RealmThreadCommunication(
            self, realm_dest_address, realm_dest_port
        )
        return {"status": "OK"}
    
    def recv_private_realm_message(self, realm_id, username_from, username_dest, message, data):
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)
        if s_fr == False or s_to == False:
            return {"status": "ERROR", "message": "User Tidak Ditemukan"}
        message = {"msg_from": s_fr["nama"], "msg_to": s_to["nama"], "msg": message}
        
        # Store the message in the incoming queue of the recipient
        inqueue_receiver = s_to['incoming']
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from] = Queue()
            inqueue_receiver[username_from].put(message)

        return {"status": "OK", "message": "Message Received"}
    
    def recv_join_group_realm(self, usernamefrom, groupname):
        if groupname not in self.group:
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}
        if usernamefrom in [member['username'] for member in self.group[groupname]['members']]:
            return {'status': 'ERROR', 'message': 'User sudah dalam group'}
        
        self.group[groupname]['members'].append({'username': usernamefrom, 'realm': 'remote'})
        return {'status': 'OK', 'message': 'Join group successful'}
    
    def list_group_members(self, sessionid, groupname):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if groupname not in self.group:
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}
        members = self.group[groupname]['members']
        return {'status': 'OK', 'members': members}        

