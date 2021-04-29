'''
message format
{
    "method":"CONNECT/LOGIN/LOGOUT/SEND",
    "token":"user token", #!required ALL except CONNECT
    "username":"username", #!required ALL except CONNECT
    "room":"room name", #!required LOGIN
    "msg":"message" #!required SEND
}
'''
from datetime import datetime
import threading
import argparse
import secrets
import random
import socket
import json
import sys


parser = argparse.ArgumentParser(description='Hi, Anon server side')
parser.add_argument('--ip', metavar='IP ADDRESS', required=True,
                    help='Input server IP Address')
parser.add_argument('-p', metavar='PORT', required=True,
                    help='Input server port')

arg = parser.parse_args()

IP_ADDRESS = arg.ip
PORT = int(arg.p)


class Rooms:
    welcomeMsg = ["Welcome {}, say hi!",
                  "{} hooped into this room",
                  "{} just slid to this room",
                  "Glad you are here, {}}",
                  "Welcome {}, we hope you brought pizza"]

    def __init__(self, roomName, socket):
        self.__roomName = roomName
        self.__userList = []
        self.socket = socket

        log(f"Created room {self.__roomName}")

    def __del__(self):
        log(f"Room {self.__roomName} deleted")

    def get_user_count(self):
        return len(self.__userList)

    def addUser(self, addr, username):
        welcomemsg = random.choice(self.welcomeMsg)

        self.__userList.append(addr)
        self.broadcast(welcomemsg.format(username), addr)

    def delUser(self, addr, username):
        self.__userList.remove(addr)
        self.broadcast(f"{username} leave the room", addr)

    def broadcast(self, msg, addr, username=None):
        if username is not None:
            log(f"{username}({self.__roomName}) > {msg}")
        else:
            log(msg)

        msg = msg.encode('utf-8')

        for user_addr in self.__userList:
            if addr != user_addr:
                self.socket.sendto(msg, user_addr)


class UDPServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.__userList = dict()
        self.__roomList = dict()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.socket.bind((self.ip, self.port))

        log(f"Server running on {self.ip}:{self.port}")
        self.listen()

    def stop(self):
        log("Server stopped")
        self.server_broadcast("Server has been stopped")
        self.socket.close()
        sys.exit()

    def server_broadcast(self, msg):
        msg = msg.encode('utf-8')

        for user in list(self.__userList.keys()):
            self.socket.sendto(msg, self.__userList[user][0])

    def send_token(self, addr):
        token = secrets.token_urlsafe(8)
        log(f"{addr[0]}:{addr[1]} connected to this server")
        self.socket.sendto(token.encode('utf-8'), addr)

    def user_login(self, addr, data):
        username = data['username']
        room = data['room']
        token = data['token']

        if username not in self.__userList.keys():
            if room not in self.__roomList:
                self.__roomList[room] = Rooms(
                    room, self.socket)

            userConf = [addr, room, token]
            self.__userList[username] = userConf
            self.__roomList[room].addUser(addr, username)
            log(
                f"{addr[0]}:{addr[1]} with username {username} joined to {room}")

            return

        self.socket.sendto("[!USRUNAVL]".encode('utf-8'), addr)

    def user_logout(self, addr, data):
        token = data['token']
        username = data['username']
        user_room = self.__userList[username][1]
        user_token = self.__userList[username][2]

        if token == user_token:
            self.__roomList[user_room].delUser(addr, username)
            del self.__userList[username]

            if self.__roomList[user_room].get_user_count() == 0:
                del self.__roomList[user_room]

    def send_msg(self, addr, data):
        msg = data["msg"]
        token = data['token']
        username = data['username']

        user_room = self.__userList[username][1]
        user_token = self.__userList[username][2]

        if token == user_token:
            self.__roomList[user_room].broadcast(
                msg, addr, username)

    def listen(self):
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                data = data.decode('utf-8')
                data = json.loads(data)
                method = data["method"]

                if method == "CONNECT":
                    threading.Thread(target=self.send_token,
                                     args=(addr,)).start()

                elif method == "LOGIN":
                    threading.Thread(target=self.user_login,
                                     args=(addr, data,)).start()

                elif method == "LOGOUT":
                    threading.Thread(target=self.user_logout,
                                     args=(addr, data)).start()

                elif method == "SEND":
                    threading.Thread(target=self.send_msg,
                                     args=(addr, data)).start()

            except Exception as e:
                log(e)


def log(msg):
    time = datetime.now()

    time = time.strftime("%H:%M:%S")
    print(f"[{time}] {msg}")


server = UDPServer(IP_ADDRESS, PORT)
server.start()
