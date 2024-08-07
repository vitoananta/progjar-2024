import logging
import uuid
import json
from queue import Queue

class Chat:
    def __init__(self, realm_connector=None):
        self.sessions = {}
        self.users = {}
        self.group = {}
        self.realm_connector = realm_connector
        self.users['messi'] = {'nama': 'Lionel Messi', 'password': 'surabaya', 'realm': 'alpha', 'incoming': {}, 'outgoing': {}}
        self.users['henderson'] = {'nama': 'Jordan Henderson', 'password': 'surabaya', 'realm': 'alpha', 'incoming': {}, 'outgoing': {}}
        self.users['lineker'] = {'nama': 'Gary Lineker', 'password': 'surabaya', 'realm': 'beta', 'incoming': {}, 'outgoing': {}}

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
                realm = j[4].strip()
                logging.warning(f"REGISTER: register {username} {password}")
                return self.register_user(username, password, nama, realm)

            elif command == 'logout':
                sessionid = j[1].strip()
                return self.logout(sessionid)
            
            elif command == 'getallsessions':
                sessionid = j[1].strip()
                logging.warning(f"GETALLSESSIONS: {sessionid}")
                return self.get_all_sessions()

            elif command == 'getdetailsession':
                sessionid = j[1].strip()
                logging.warning(f"GETDETAILSESSION: {sessionid}")
                return self.get_detail_session(sessionid)

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
        if self.users[username]['realm'] != realm:
            return {'status': 'ERROR', 'message': 'User realm mismatch'}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid] = {'username': username, 'userdetail': self.users[username], 'userrealm': realm}
        return {'status': 'OK', 'tokenid': tokenid}

    def register_user(self, username, password, nama, realm):
        if username in self.users:
            return {'status': 'ERROR', 'message': 'User already exists'}
        nama = nama.replace("_", " ")
        self.users[username] = {
            'nama': nama,
            'password': password,
            'realm': realm,
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
    
    def get_user_by_nama(self, nama):
        for username, user in self.users.items():
            if user['nama'] == nama:
                return username
        return False
    
    def get_all_sessions(self):
        def convert_queues(obj):
            if isinstance(obj, Queue):
                return list(obj.queue)
            elif isinstance(obj, dict):
                return {k: convert_queues(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_queues(i) for i in obj]
            else:
                return obj
        
        sessions_copy = {}
        for session_id, session_data in self.sessions.items():
            session_data_copy = {
                'username': session_data['username'],
                'userdetail': convert_queues(session_data['userdetail']),
                'userrealm': session_data['userrealm']
            }
            sessions_copy[session_id] = session_data_copy
        
        return {'status': 'OK', 'sessions': sessions_copy}

    def get_detail_session(self, sessionid):
        def convert_queues(obj):
            if isinstance(obj, Queue):
                return list(obj.queue)
            elif isinstance(obj, dict):
                return {k: convert_queues(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_queues(i) for i in obj]
            else:
                return obj
        
        if sessionid in self.sessions:
            session_data = self.sessions[sessionid]
            session_data_copy = {
                'username': session_data['username'],
                'userdetail': convert_queues(session_data['userdetail']),
                'userrealm': session_data['userrealm']
            }
            return {'status': 'OK', 'session': session_data_copy}
        else:
            return {'status': 'ERROR', 'message': 'Session not found'}

    def send_message(self, sessionid, username_from, username_dest, message):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session not found'}
        sender = self.get_user(username_from)
        receiver = self.get_user(username_dest)

        if not sender:
            return {'status': 'ERROR', 'message': 'Sender not found'}

        if not receiver:
            return {'status': 'ERROR', 'message': 'Receiver not found'}

        if sender['realm'] != receiver['realm']:
            # Cross-realm messaging
            if self.realm_connector:
                # Send message to the other realm
                return self.realm_connector.send_cross_realm_message(username_from, username_dest, message)
            else:
                return {'status': 'ERROR', 'message': 'No realm connector available'}

        # Local message handling
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
    
    def send_message_cross_realm(self, message):
        username_from = message['username_from']
        username_dest = message['username_dest']
        msg = message['message']

        sender = self.get_user(username_from)
        receiver = self.get_user(username_dest)

        if not sender or not receiver:
            return {'status': 'ERROR', 'message': 'User not found'}

        message = {'msg_from': sender['nama'], 'msg_to': receiver['nama'], 'msg': msg}
        outqueue_sender = sender['outgoing']
        inqueue_receiver = receiver['incoming']
        if sender['nama'] not in outqueue_sender:
            outqueue_sender[sender['nama']] = Queue()
        outqueue_sender[sender['nama']].put(message)
        if sender['nama'] not in inqueue_receiver:
            inqueue_receiver[sender['nama']] = Queue()
        inqueue_receiver[sender['nama']].put(message)
        return {'status': 'OK', 'message': 'Cross-realm message sent'}


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
    
        # Check if the group exists in the current realm
        if groupname not in self.group:
            # Assume the group exists in the other realm
            if self.realm_connector:
                username = self.sessions[sessionid]['username']
                return self.realm_connector.forward_group_command('joingroup', username, groupname)
            else:
                return {'status': 'ERROR', 'message': 'Group not found'}
        
        if self.sessions[sessionid]['username'] in self.group[groupname]['members']:
            return {'status': 'ERROR', 'message': 'Already a member'}
        self.group[groupname]['members'].append(self.sessions[sessionid]['username'])
        return {'status': 'OK', 'message': 'Joined group'}
    

    def proses_crossrealm(self, command, message):
        if command == 'joingroup':
            username = message['username']
            groupname = message['groupname']
            if groupname in self.group:
                if username in self.group[groupname]['members']:
                    return {'status': 'ERROR', 'message': 'Already a member'}
                self.group[groupname]['members'].append(username)
                return {'status': 'OK', 'message': 'Joined group'}
            else:
                return {'status': 'ERROR', 'message': 'Group not found'}
        elif command == 'sendgroup':
            groupname = message['groupname']
            sender_name = message['sender_name']
            receiver_name = message['receiver_name']
            msg = message['message']
            
            if receiver_name:
                receiver_username = self.get_user_by_nama(receiver_name)
                if not receiver_username:
                    return {'status': 'ERROR', 'message': 'Receiver not found'}
                
                receiver = self.get_user(receiver_username)
                group_message = {'group': groupname, 'msg_from': sender_name, 'msg_to': receiver_name, 'msg': msg}
                
                if sender_name not in receiver['incoming']:
                    receiver['incoming'][sender_name] = Queue()
                receiver['incoming'][sender_name].put(group_message)
            else:
                # Broadcast to all group members
                if groupname not in self.group:
                    return {'status': 'ERROR', 'message': 'Group not found'}
                
                group_message = {'group': groupname, 'msg_from': sender_name, 'msg': msg}
                
                for member in self.group[groupname]['members']:
                    if member != sender_name:
                        receiver = self.get_user(member)
                        message_to_send = group_message.copy()
                        message_to_send['msg_to'] = receiver['nama']
                        
                        if sender_name not in receiver['incoming']:
                            receiver['incoming'][sender_name] = Queue()
                        receiver['incoming'][sender_name].put(message_to_send)
            
            return {'status': 'OK', 'message': 'Group message received'}
        
        return {'status': 'ERROR', 'message': 'Invalid command'}



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
            # Try to forward the message to the other realm if the group is not found
            if self.realm_connector:
                sender = self.get_user(self.sessions[sessionid]['username'])
                return self.realm_connector.send_cross_realm_group_message(
                    groupname, sender['nama'], None, message
                )
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

            # Check if receiver is in the same realm or different realm
            if sender['realm'] == receiver['realm']:
                # Add to receiver's incoming queue
                if sender['nama'] not in receiver['incoming']:
                    receiver['incoming'][sender['nama']] = Queue()
                receiver['incoming'][sender['nama']].put(message_to_send)
            else:
                # Forward to the other realm
                if self.realm_connector:
                    self.realm_connector.send_cross_realm_group_message(groupname, sender['nama'], receiver['nama'], message)

        return {'status': 'OK', 'message': 'Message sent to group'}

    def send_cross_realm_group_message(self, groupname, sender_name, receiver_name, message):
        try:
            if not self.connection:
                return {'status': 'ERROR', 'message': 'No connection to target realm'}
            
            message = json.dumps({
                'command': 'crossrealm_sendgroup',
                'groupname': groupname,
                'sender_name': sender_name,
                'receiver_name': receiver_name,  # Allow null to broadcast to all members
                'message': message
            }) + "\r\n"
            
            self.connection.sendall(message.encode())
            
            # Wait for response
            response = self.connection.recv(512).decode().strip()
            return json.loads(response)
            
        except Exception as e:
            logging.error(f"Failed to send group message to other realm: {e}")
            return {'status': 'ERROR', 'message': 'Failed to send group message to other realm'}
