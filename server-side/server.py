'''
message format
{
    "method":"CONNECT/LOGIN/LOGOUT/SEND",
    "token":"user token",
    "username":"username",
    "room":"room name",
}
'''

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

        log(f"Created room {self.__roomName}")

    def __del__(self):
        log(f"Room {self.__roomName} deleted")

    def addUser(self, addr, username):
        self.__userList.append(addr)
        self.broadcast(f"Welcome {username}, say hi!", addr)

    def delUser(self, addr, username):
        self.__userList.remove(addr)
        self.broadcast(f"{username} leave the room", addr)

    def broadcast(self, msg, addr, username=None):
        if username is not None:
            log(f"{username}({self.__roomName}) > {msg}")
        else:
            log(msg)

        msg = msg.encode('utf-8')

        for user in self.__userList:
            if username != user:
                self.socket.sendto(msg, user)


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

    def get_user_count(self):
        return len(self.__userList)

    def listen(self):
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                data = data.decode('utf-8')
                data = json.loads(data)
                method = data["method"]

                if method == "CONNECT":
                    token = secrets.token_urlsafe(8)
                    log(f"{addr[0]}:{addr[1]} connected to this server")
                    self.socket.sendto(token.encode('utf-8'), addr)

                else:
                    username = data["username"]
                    token = data["token"]

                    if method == "LOGIN":
                        room = data["room"]
                        if username not in self.__userList.keys():
                            if room not in self.__roomList:
                                self.__roomList[room] = Rooms(
                                    room, self.socket)

                            userConf = [addr, room, token]
                            self.__userList[username] = userConf
                            self.__roomList[room].addUser(addr, username)
                            log(
                                f"{addr[0]}:{addr[1]} with username {username} joined to {room}")
                            continue

                        self.socket.sendto("[!USRUNAVL]".encode('utf-8'), addr)

                    elif method == "LOGOUT":
                        user_room = self.__userList[username][1]
                        user_token = self.__userList[username][2]

                        if token == user_token:
                            self.__roomList[user_room].delUser(addr, username)
                            del self.__userList[username]

                            if self.__roomList[user_room].get_user_count() == 0:
                                del self.__roomList[user_room]

                    elif method == "SEND":
                        msg = data["msg"]
                        user_room = self.__userList[username][1]
                        user_token = self.__userList[username][2]

                        if token == user_token:
                            self.__roomList[user_room].broadcast(
                                msg, addr, username)

                    else:
                        log(msg)
            except Exception as e:
                log(e)
                continue


def log(msg):
    time = datetime.time()

    time = time.strftime("%H:%M:%S")
    print(f"[{time}] {msg}")


server = UDPServer(IP_ADDRESS, PORT)
server.start()
