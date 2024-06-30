import socket
import json
from chat import Chat

class ChatClient:
    def __init__(self, TARGET_IP, TARGET_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""

    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            
            if (command=='register'):
                username=j[1].strip()
                password=j[2].strip()
                nama=j[3].strip()
                negara=j[4].strip()
                return self.register(username, password, nama, negara)
             
            elif (command=='logout'):
                return self.logout()
            
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                    message="{} {}" . format(message,w)
                return self.send_message(usernameto,message)
            
            elif (command=='inbox'):
                return self.inbox()

            elif (command=='creategroup'):
                groupname = j[1].strip()
                return self.create_group(groupname)
            
            elif (command=='joingroup'):
                groupname = j[1].strip()
                return self.join_group(groupname)
            
            elif command == "joingrouprealm":
                realmid = j[1].strip()
                groupname = j[2].strip()
                return self.join_group_realm(realmid, groupname)

            elif (command=='sendgroup'):
                groupname = j[1].strip()
                message=""
                for w in j[2:]:
                    message="{} {}" . format(message,w)
                return self.send_group_message(groupname,message)

            elif command == "addrealm":
                realmid = j[1].strip()
                realm_address = j[2].strip()
                realm_port = j[3].strip()
                return self.add_realm(realmid, realm_address, realm_port)

            elif command == "sendrealm":
                realmid = j[1].strip()
                username_to = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}".format(message, w)
                return self.send_realm_message(realmid, username_to, message)
            
            elif command == "listmembers":
                groupname = j[1].strip()
                return self.list_members(groupname)
            
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
            return "-Maaf, command tidak benar"

    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(32)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}

    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    
    def register(self,username,password, nama, negara):
        string="register {} {} {} {}\r\n" . format(username,password, nama, negara)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} register in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
        
    def logout(self):   
        string="logout {}\r\n".format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=""
            return "Logout Berhasil"
        else:
            return "Error, {}" . format(result['message'])
    
    def send_message(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
        
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])

    def create_group(self, groupname):
        string="creategroup {} {} \r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Group {} added".format(groupname)
    
    def join_group(self, groupname):
        string="joingroup {} {} \r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Group {} added".format(groupname)
        
    def join_group_realm(self, realmid, groupname):
        string = "joingrouprealm {} {} {} \r\n".format(self.tokenid, realmid, groupname)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "Group {} added".format(groupname)
        else:
            return "Error, {}".format(result["message"])

    def send_group_message(self,groupname="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgroup {} {} {} \r\n" . format(self.tokenid,groupname,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
        
    def add_realm(self, realmid, realm_address, realm_port):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "addrealm {} {} {} \r\n".format(realmid, realm_address, realm_port)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "Realm {} added".format(realmid)
        else:
            return "Error, {}".format(result["message"])
        
    def send_realm_message(self, realmid, username_to, message):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "sendrealm {} {} {} {}\r\n".format(
            self.tokenid, realmid, username_to, message
        )
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "Message sent to realm {}".format(realmid)
        else:
            return "Error, {}".format(result["message"])
        
    def list_members(self, groupname):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "listmembers {} {} \r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "Members of group {}: {}".format(groupname, result["members"])
        else:
            return "Error, {}".format(result["message"])

if __name__=="__main__":
    TARGET_IP = input("Berikan target IP (misal, 127.0.0.1): ")
    TARGET_PORT = int(input("Berikan target port (misal, 8889): "))

    cc = ChatClient(TARGET_IP, TARGET_PORT)
    c = Chat()

    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))