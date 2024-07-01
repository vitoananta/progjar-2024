import threading
import socket
import json
import logging
import uuid
from queue import Queue

class RealmThreadCommunication(threading.Thread):
    def __init__(self, chats, realm_dest_address, realm_dest_port):
        super().__init__()
        self.chats = chats
        self.chat = {}
        self.realm_dest_address = realm_dest_address
        self.realm_dest_port = realm_dest_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.realm_dest_address, self.realm_dest_port))

    def send_string(self, string):
        try:
            self.sock.sendall(string.encode())
            recv_msg = ""
            while True:
                data = self.sock.recv(32)
                if data:
                    recv_msg += data.decode()
                    if recv_msg[-4:] == '\r\n\r\n':
                        return json.loads(recv_msg)
        except Exception as e:
            logging.error(f"Error: {e}")
            self.sock.close()
            return {'status': 'ERROR', 'message': 'Failed'}

    def put(self, message):
        dest = message["msg_to"]
        if dest not in self.chat:
            self.chat[dest] = Queue()
        self.chat[dest].put(message)


class Chat:
    def __init__(self):
        self.sessions = {}
        self.users = {}
        self.group = {}
        self.users['messi'] = {'nama': 'Lionel Messi', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
        self.users['henderson'] = {'nama': 'Jordan Henderson', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
        self.users['lineker'] = {'nama': 'Gary Lineker', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
        self.realm_communication_threads = []

    def proses(self, data):
        j = data.split(" ")
        try:
            command = j[0].strip()
            if command == 'auth':
                username = j[1].strip()
                password = j[2].strip()
                realm = j[3].strip()
                logging.warning(f"AUTH: auth {username} {password} {realm}")
                return self.autentikasi_user(username, password, realm)

            elif command == 'register':
                username = j[1].strip()
                password = j[2].strip()
                nama = j[3].strip()
                logging.warning(f"REGISTER: register {username} {password}")
                return self.register_user(username, password, nama)

            elif command == 'logout':
                sessionid = j[1].strip()
                return self.logout(sessionid)

            elif command == 'getsessiondetails':
                sessionid = j[1].strip()
                logging.warning(f"GETSESSIONDETAILS: {sessionid}")
                return self.get_session_details(sessionid)

            elif command == 'send':
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message = " ".join(j[3:])
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning(f"SEND: session {sessionid} send message from {usernamefrom} to {usernameto}")
                return self.send_message(sessionid, usernamefrom, usernameto, message)

            elif command == 'inbox':
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                logging.warning(f"INBOX: {sessionid}")
                return self.get_inbox(username)

            elif command == 'creategroup':
                sessionid = j[1].strip()
                groupname = j[2].strip()
                logging.warning(f"CREATEGROUP: {sessionid} create group {groupname}")
                return self.create_group(sessionid, groupname)

            elif command == 'joingroup':
                sessionid = j[1].strip()
                groupname = j[2].strip()
                logging.warning(f"JOINGROUP: {sessionid} join group {groupname}")
                return self.join_group(sessionid, groupname)

            elif command == 'leavegroup':
                sessionid = j[1].strip()
                groupname = j[2].strip()
                logging.warning(f"LEAVEGROUP: {sessionid} leave group {groupname}")
                return self.leave_group(sessionid, groupname)

            elif command == 'sendgroup':
                sessionid = j[1].strip()
                groupname = j[2].strip()
                message = " ".join(j[3:])
                logging.warning(f"SENDGROUP: {sessionid} send message to group {groupname}")
                return self.send_group_message(sessionid, groupname, message)

            elif command == 'getgroupmember':
                groupname = j[1].strip()
                return self.get_group_member(groupname)

            elif command == 'connectrealms':
                alpha_address = j[1].strip()
                alpha_port = int(j[2].strip())
                beta_address = j[3].strip()
                beta_port = int(j[4].strip())
                return self.check_and_establish_realm_connection(alpha_address, alpha_port, beta_address, beta_port)

            elif command == 'getallsessions':
                return self.get_all_sessions()

            else:
                logging.warning(command)
                return {"status": "ERROR", "message": "**Invalid protocol"}
        except KeyError:
            return {'status': 'ERROR', 'message': 'Information not found'}
        except IndexError:
            return {'status': 'ERROR', 'message': '--Invalid protocol'}

    def autentikasi_user(self, username, password, realm):
        if username not in self.users:
            return {'status': 'ERROR', 'message': 'User not found'}
        if self.users[username]['password'] != password:
            return {'status': 'ERROR', 'message': 'Incorrect password'}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid] = {'username': username, 'userdetail': self.users[username], 'userrealm': realm}
        return {'status': 'OK', 'tokenid': tokenid}

    def register_user(self, username, password, nama):
        if username in self.users:
            return {'status': 'ERROR', 'message': 'User already exists'}
        nama = nama.replace("_", " ")
        self.users[username] = {
            'nama': nama,
            'password': password,
            'incoming': {},
            'outgoing': {}
        }
        return {'status': 'OK', 'message': 'User registered'}

    def logout(self, sessionid):
        if sessionid in self.sessions:
            del self.sessions[sessionid]
            return {'status': 'OK'}
        else:
            return {'status': 'ERROR', 'message': 'Not logged in'}

    def get_user(self, username):
        return self.users.get(username, False)

    def get_session_details(self, sessionid):
        if sessionid in self.sessions:
            return {'status': 'OK', 'session': self.sessions[sessionid]}
        else:
            return {'status': 'ERROR', 'message': 'Session not found'}

    def send_message(self, sessionid, username_from, username_dest, message):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session not found'}
        sender = self.get_user(username_from)
        receiver = self.get_user(username_dest)

        if not sender or not receiver:
            return {'status': 'ERROR', 'message': 'User not found'}

        message = {'msg_from': sender['nama'], 'msg_to': receiver['nama'], 'msg': message}
        outqueue_sender = sender['outgoing']
        inqueue_receiver = receiver['incoming']
        if sender['nama'] not in outqueue_sender:
            outqueue_sender[sender['nama']] = Queue()
        outqueue_sender[sender['nama']].put(message)
        if sender['nama'] not in inqueue_receiver:
            inqueue_receiver[sender['nama']] = Queue()
        inqueue_receiver[sender['nama']].put(message)
        return {'status': 'OK', 'message': 'Message sent'}

    def get_inbox(self, username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs = {}
        for user in incoming:
            msgs[user] = []
            while not incoming[user].empty():
                msgs[user].append(incoming[user].get_nowait())
        return {'status': 'OK', 'messages': msgs}

    def create_group(self, sessionid, groupname):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session not found'}
        if groupname in self.group:
            return {'status': 'ERROR', 'message': 'Group already exists'}
        self.group[groupname] = {
            'admin': self.sessions[sessionid]['username'],
            'members': [],
            'messages': []
        }
        self.group[groupname]['members'].append(self.sessions[sessionid]['username'])
        return {'status': 'OK', 'message': 'Group created'}

    def join_group(self, sessionid, groupname):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session not found'}
        if groupname not in self.group:
            return {'status': 'ERROR', 'message': 'Group not found'}
        if self.sessions[sessionid]['username'] in self.group[groupname]['members']:
            return {'status': 'ERROR', 'message': 'Already a member'}
        self.group[groupname]['members'].append(self.sessions[sessionid]['username'])
        return {'status': 'OK', 'message': 'Joined group'}

    def leave_group(self, sessionid, groupname):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session not found'}
        if groupname not in self.group:
            return {'status': 'ERROR', 'message': 'Group not found'}
        if self.sessions[sessionid]['username'] not in self.group[groupname]['members']:
            return {'status': 'ERROR', 'message': 'Not a member'}
        self.group[groupname]['members'].remove(self.sessions[sessionid]['username'])
        return {'status': 'OK', 'message': 'Left group'}

    def send_group_message(self, sessionid, groupname, message):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session not found'}
        if groupname not in self.group:
            return {'status': 'ERROR', 'message': 'Group not found'}
        if self.sessions[sessionid]['username'] not in self.group[groupname]['members']:
            return {'status': 'ERROR', 'message': 'Not a member'}

        sender = self.get_user(self.sessions[sessionid]['username'])
        group_message = {'group': groupname, 'msg_from': sender['nama'], 'msg': message}

        for receiver_username in self.group[groupname]['members']:
            receiver = self.get_user(receiver_username)
            message_to_send = group_message.copy()
            message_to_send['msg_to'] = receiver['nama']

            # Add to sender's outgoing queue
            if sender['nama'] not in sender['outgoing']:
                sender['outgoing'][sender['nama']] = Queue()
            sender['outgoing'][sender['nama']].put(message_to_send)

            # Add to receiver's incoming queue
            if sender['nama'] not in receiver['incoming']:
                receiver['incoming'][sender['nama']] = Queue()
            receiver['incoming'][sender['nama']].put(message_to_send)

        return {'status': 'OK', 'message': 'Message sent to group'}

    def get_group_member(self, groupname):
        if groupname in self.group:
            return {'status': 'OK', 'members': self.group[groupname]['members']}
        else:
            return {'status': 'ERROR', 'message': 'Group not found'}

    def check_and_establish_realm_connection(self, alpha_address, alpha_port, beta_address, beta_port):
        try:
            alpha_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            alpha_socket.connect((alpha_address, alpha_port))
            alpha_socket.close()
        except Exception as e:
            logging.error(f"Failed to connect to alpha server: {e}")
            return {'status': 'ERROR', 'message': 'Alpha server is not up'}

        try:
            beta_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            beta_socket.connect((beta_address, beta_port))
            beta_socket.close()
        except Exception as e:
            logging.error(f"Failed to connect to beta server: {e}")
            return {'status': 'ERROR', 'message': 'Beta server is not up'}

        # Both servers are up, establish communication threads
        alpha_communication_thread = RealmThreadCommunication(self, alpha_address, alpha_port)
        beta_communication_thread = RealmThreadCommunication(self, beta_address, beta_port)
        
        alpha_communication_thread.start()
        beta_communication_thread.start()
        
        self.realm_communication_threads.append(alpha_communication_thread)
        self.realm_communication_threads.append(beta_communication_thread)

        return {'status': 'OK', 'message': 'Connection established between alpha and beta servers'}

    def get_all_sessions(self):
        return {'status': 'OK', 'sessions': self.sessions}

