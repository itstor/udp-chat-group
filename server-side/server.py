from datetime import datetime
import threading
import argparse
import secrets
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
    def __init__(self, roomName, socket):
        self.__roomName = roomName
        self.__userList = []
        self.socket = socket

    def addUser(self, addr, username):
        self.__userList.append(addr)
        self.broadcast(f"Welcome {username}, say hi!", addr)

    def delUser(self, addr, username):
        self.__userList.remove(addr)
        self.broadcast(f"{username} leave the room", addr)

    def broadcast(self, msg, addr):
        for user in self.__userList:
            socket.sendto(msg, user)


class UDPServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.__userList = dict()
        self.__roomList = dict()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.socket.bind((self.ip, self.port))

        self.log(f"Server running on {self.ip}:{self.port}")
        self.listen()

    def stop(self):
        self.log("Server stopped")
        self.server_broadcast("Server has been stopped")
        self.socket.close()
        sys.exit()

    def log(self, msg):
        now = datetime.now()

        now = now.strftime("%H: %M: %S")
        print(f"[{now}] {msg}")

    def server_broadcast(self, msg):
        msg = msg.encode('utf-8')
        for user in list(self.__userList.keys()):
            self.socket.sendto(msg, self.__userList[user][0])

    def listen(self):
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                data = data.decode('utf-8')
                data = json.loads(data)
                method = data["method"]

                if method == "CONNECT":
                    token = secrets.token_urlsafe(16)
                    self.log(f"{addr[0]}:{addr[1]} connected to this server")
                    self.socket.sendto(token.encode('utf-8'), addr)

                else:
                    room = data["room"]
                    username = data["username"]
                    msg = data["msg"].encode('utf-8')

                    if method == "LOGIN":
                        if username not in self.__userList.keys():
                            if room not in self.__roomList:
                                self.__roomList[room] = Rooms(
                                    room, self.socket)

                            userConf = [addr, room]
                            self.__userList[username] = userConf
                            self.__roomList[room].addUser(addr, username)
                            self.log(
                                f"{addr[0]}:{addr[1]} with username {username} joined to {room}")
                            continue

                        self.socket.sendto("[!USRUNAVL]".encode('utf-8'), addr)

                    elif method == "LOGOUT":
                        user_room = self.__userList[username][1]

                        self.__roomList[user_room].delUser(addr, username)
                        del self.__userList[username]

                    elif method == "SEND":
                        user_room = self.__userList[username][1]

                        self.__roomList[user_room].broadcast(msg, addr)
                        self.log(f"{username}({room}) > {msg.decode('utf-8')}")

                    else:
                        self.log(msg)
            except Exception as e:
                print(e)
                continue


server = UDPServer(IP_ADDRESS, PORT)
print("HELLO")
server.start()
