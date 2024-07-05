import socket
import json

ALPHA_ADDRESS = '127.0.0.1'
ALPHA_PORT = 9993
BETA_ADDRESS = '127.0.0.1'
BETA_PORT = 8889

class ChatClient:
    def __init__(self, target_ip, target_port, realm):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (target_ip, target_port)
        self.sock.connect(self.server_address)
        self.tokenid = ""
        self.realm = realm

    def proses(self, cmdline):
        j = cmdline.split(" ")
        try:
            command = j[0].strip()
            if command == 'auth':
                username = j[1].strip()
                password = j[2].strip()
                return self.login(username, password)
            
            if command == 'register':
                username = j[1].strip()
                password = j[2].strip()
                nama = j[3].strip()
                realm = self.realm
                return self.register(username, password, nama, realm)
             
            elif command == 'logout':
                return self.logout()
            
            elif command == 'getallsessions':
                return self.get_all_sessions()
            
            elif command == 'getdetailsession':
                return self.get_detail_session()
            
            elif command == 'send':
                usernameto = j[1].strip()
                message = " ".join(j[2:])
                return self.send_message(usernameto, message)
            
            elif command == 'inbox':
                return self.inbox()
            
            elif command == 'creategroup':
                groupname = j[1].strip()
                return self.create_group(groupname)
            
            elif command == 'joingroup':
                groupname = j[1].strip()
                return self.join_group(groupname)
            
            elif command == 'leavegroup':
                groupname = j[1].strip()
                return self.leave_group(groupname)
            
            elif command == 'sendgroup':
                groupname = j[1].strip()
                message = " ".join(j[2:])
                return self.send_group_message(groupname, message)
            
            elif command == 'getgroupmember':
                groupname = j[1].strip()
                return self.get_group_members(groupname)

            else:
                return "*Maaf, command tidak benar"
        except IndexError:
            return "-Maaf, command tidak benar"

    def send_string(self, string):
        try:
            self.sock.sendall(string.encode())
            receive_msg = ""
            while True:
                data = self.sock.recv(512)
                print("Received from server:", data)
                if data:
                    receive_msg += data.decode()  # Data must be decoded to operate as a string
                    if receive_msg[-4:] == '\r\n\r\n':
                        print("End of string")
                        return json.loads(receive_msg)
        except Exception as e:
            print(f"Error: {e}")
            self.sock.close()
            return {'status': 'ERROR', 'message': 'Failed'}

    def login(self, username, password):
        string = f"auth {username} {password} {self.realm} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            self.tokenid = result['tokenid']
            return f"Username {username} logged in, token {self.tokenid}"
        else:
            return f"Error, {result['message']}"
    
    def register(self, username, password, nama, realm):
        string = f"register {username} {password} {nama} {realm}\r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return f"Username {username} registered"
        else:
            return f"Error, {result['message']}"
        
    def logout(self):   
        string = f"logout {self.tokenid}\r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            self.tokenid = ""
            return "Logout successful"
        else:
            return f"Error, {result['message']}"
        
    def get_all_sessions(self):
        string = "getallsessions \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return json.dumps(result['sessions'])
        else:
            return f"Error, {result['message']}"
    
    def get_detail_session(self):
        string = f"getdetailsession {self.tokenid} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return json.dumps(result['session'])
        else:
            return f"Error, {result['message']}"
        
    def send_message(self, usernameto="", message=""):
        if not self.tokenid:
            return "Error, not authorized"
        string = f"send {self.tokenid} {usernameto} {message} \r\n"
        print(string)
        result = self.send_string(string)
        if result['status'] == 'OK':
            return f"Message sent to {usernameto}"
        else:
            return f"Error, {result['message']}"
        
    def inbox(self):
        if not self.tokenid:
            return "Error, not authorized"
        string = f"inbox {self.tokenid} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return json.dumps(result['messages'])
        else:
            return f"Error, {result['message']}"
        
    def create_group(self, groupname):
        if not self.tokenid:
            return "Error, not authorized"
        string = f"creategroup {self.tokenid} {groupname} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return f"Group {groupname} created"
        else:
            return f"Error, {result['message']}"
        
    def join_group(self, groupname):
        if not self.tokenid:
            return "Error, not authorized"
        string = f"joingroup {self.tokenid} {groupname} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return f"Joined group {groupname}"
        else:
            return f"Error, {result['message']}"
        
    def leave_group(self, groupname):
        if not self.tokenid:
            return "Error, not authorized"
        string = f"leavegroup {self.tokenid} {groupname} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return f"Left group {groupname}"
        else:
            return f"Error, {result['message']}"
        
    def send_group_message(self, groupname, message):
        if not self.tokenid:
            return "Error, not authorized"
        string = f"sendgroup {self.tokenid} {groupname} {message} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return f"Message sent to group {groupname}"
        else:
            return f"Error, {result['message']}"
        
    def get_group_members(self, groupname):
        string = f"getgroupmember {groupname} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return json.dumps(result['members'])
        else:
            return f"Error, {result['message']}"

    def connect_realms(self, alpha_address, alpha_port, beta_address, beta_port):
        string = f"connectrealms {alpha_address} {alpha_port} {beta_address} {beta_port} \r\n"
        result = self.send_string(string)
        if result['status'] == 'OK':
            return "Connection established between alpha and beta servers"
        else:
            return f"Error, {result['message']}"

if __name__ == "__main__":
    realm = input("Choose realm (alpha/beta): ")
    target_ip = "127.0.0.1"
    if realm == "alpha":
        target_port = ALPHA_PORT
    elif realm == "beta":
        target_port = BETA_PORT
    else:
        print("Realm not found")
        exit()

    cc = ChatClient(target_ip, target_port, realm)
    
    while True:
        cmdline = input(f"Command {cc.tokenid}: ")
        print(cc.proses(cmdline))