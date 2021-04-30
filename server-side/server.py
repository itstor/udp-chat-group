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
import tkinter.scrolledtext
import threading
import argparse
import secrets
import tkinter
import random
import socket
import time
import json
import sys


parser = argparse.ArgumentParser(description='Hi, Anon server side')
parser.add_argument('-l', '--ip-address', dest='ip', metavar='IP ADDRESS', required=True,
                    help='Input server IP Address')
parser.add_argument('-p', '--port', dest='port', metavar='PORT', required=True,
                    help='Input server port')
parser.add_argument('--no-gui', dest='no_gui', action='store_true',
                    help='Set interface to CLI')

arg = parser.parse_args()

IP_ADDRESS = arg.ip
PORT = int(arg.port)
ISGUI = not arg.no_gui


class Window:
    def __init__(self, server):
        self.server = server

    def gui(self):
        self.window = tkinter.Tk()
        self.window.title(f"Hi, Anon! Server [{IP_ADDRESS}:{PORT}]")

        self.serverLabel = tkinter.Label(self.window, text=f"Hi, Anon! server")
        self.serverLabel.config(font=('Arial', 12))
        self.serverLabel.pack(padx=20, pady=20)

        self.log = tkinter.scrolledtext.ScrolledText(self.window)
        self.log.pack(padx=20, pady=5)
        self.log.config(state='disabled')

        self.stopButton = tkinter.Button(
            self.window, text="Stop Server", command=self.server.stop)
        self.stopButton.config(font=('Arial', 12))
        self.stopButton.pack(padx=20, pady=5)

        self.window.protocol('WM_DELETE_WINDOW', self.server.stop)

        self.window.mainloop()

    def add_log(self, msg):
        self.log.config(state='normal')
        self.log.insert('end', msg)
        self.log.yview('end')
        self.log.config(state='disabled')


class Rooms:
    welcomeMsg = ["Welcome {}, say hi!",
                  "{} hooped into this room",
                  "{} just slid to this room",
                  "Glad you are here, {}",
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
        self.socket.settimeout(1)

    def start(self):
        self.socket.bind((self.ip, self.port))
        self.running = True

        log(f"Server running on {self.ip}:{self.port}")
        self.listen()

    def stop(self):
        self.server_broadcast("Server has been stopped")
        self.running = False
        log("Server stopped")
        if ISGUI:
            window.window.destroy()
        self.socket.close()
        print("Server Closed")
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
            self.socket.sendto("[SUCCESS]".encode('utf-8'), addr)
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
        while self.running:
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

            except KeyboardInterrupt:
                self.stop()
            except socket.timeout:
                continue
            except Exception as e:
                log(str(e))
        else:
            print("Done")


def log(msg):
    time = datetime.now()
    time = time.strftime("%H:%M:%S")

    if ISGUI:
        window.add_log(f"[{time}]" + msg + "\n")
    else:
        print(f"[{time}] {msg}")


server = UDPServer(IP_ADDRESS, PORT)

if ISGUI:
    window = Window(server)
    window_thread = threading.Thread(target=window.gui).start()
    time.sleep(3)
    server_thread = threading.Thread(target=server.start).start()
else:
    server.start()
# server.start()
