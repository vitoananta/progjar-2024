import socket
import json

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
                return self.register(username, password, nama)
             
            elif command == 'logout':
                return self.logout()
            
            elif command == 'send':
                usernameto = j[1].strip()
                message = " ".join(j[2:])
                return self.send_message(usernameto, message)
            
            elif command == 'inbox':
                return self.inbox()
            
            elif command == 'getsessiondetails':
                return self.get_session_details()

            else:
                return "*Maaf, command tidak benar"
        except IndexError:
            return "-Maaf, command tidak benar"

    def send_string(self, string):
        try:
            self.sock.sendall(string.encode())
            receive_msg = ""
            while True:
                data = self.sock.recv(32)
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
    
    def register(self, username, password, nama):
        string = f"register {username} {password} {nama}\r\n"
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
    
    def get_session_details(self):
        string = f"getsessiondetails {self.tokenid} \r\n"
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

if __name__ == "__main__":
    realm = input("Choose realm (alpha/beta): ")
    target_ip = "127.0.0.1"
    if realm == "alpha":
        target_port = 8889
    elif realm == "beta":
        target_port = 8890
    else:
        print("Realm not found")
        exit()

    cc = ChatClient(target_ip, target_port, realm)
    
    while True:
        cmdline = input(f"Command {cc.tokenid}: ")
        print(cc.proses(cmdline))
    