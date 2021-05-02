from PySide2.QtCore import QObject, QRunnable, QThreadPool, Slot, Signal
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtGui import QGuiApplication
import socket
import json
import sys
import os

client = None
gui = None


class WorkerSignal(QObject):
    isRunning = Signal(bool)


class Worker(QRunnable):
    def __init__(self, socket):
        super(Worker, self).__init__()
        self.socket = socket
        self.signal = WorkerSignal()

        self.isRunning = self.signal.isRunning

    @Slot()
    def run(self):
        self.socket.settimeout(1)

        while self.isRunning:
            print("Listening")
            try:
                data = self.socket.recv(1024)
                data = data.decode('utf-8')
                data = json.dumps(data)

                resp = data["response"]
                msg = data["msg"]

                if resp == "LOG":
                    gui.addChatBox(msg, "server", False)

                elif resp == "MESSAGE":
                    username = data['username']
                    gui.addChatBox(msg, username, True)
            except socket.timeout:
                continue
            except Exception as e:
                print(e)


class GUI(QObject):
    def __init__(self):
        QObject.__init__(self)

    showToast = Signal(str)
    addChat = Signal(str, str, bool)
    inputMsg = Signal(str)
    moveChat = Signal(bool)
    setRoom = Signal(str)

    @Slot(str, int, str, str)
    def getInputData(self, ip, port, username, room):
        client.setup_connection(ip, port, username, room)

    @Slot(str)
    def showToastBox(self, msg):
        self.showToast.emit(msg)

    @Slot(str, str, bool)
    def addChatBox(self, msg, username, isme):
        self.addChat.emit(msg, username, isme)

    @Slot(str)
    def getInputMsg(self, text):
        client.send_msg(text)

    @Slot(bool)
    def moveToChat(self, ismove):
        self.moveChat.emit(ismove)

    @Slot(bool)
    def closeChat(self, close):
        client.user_logout()

    @Slot(str)
    def setRoomName(self, roomName):
        self.setRoom.emit(roomName)


class Client:
    def __init__(self):
        self.__token = ""
        self.running = True

        self.threadpool = QThreadPool()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def stop(self):
        self.running = False
        self.user_logout()
        sys.exit()

    def setup_connection(self, ip, port, username, room):
        self.ip = ip
        self.port = port
        self.__username = username
        self.__room = room

        if self.check_connection():
            self.socket.connect((self.ip, self.port))
            if self.user_login():
                gui.moveToChat(True)
                gui.setRoomName(self.__room)
                self.start_listen()

    def check_connection(self):
        msg = '{"method":"CONNECT"}'

        self.socket.sendto(msg.encode('utf-8'), (self.ip, self.port))
        oldTimeout = self.socket.gettimeout()
        self.socket.settimeout(10)
        try:
            token, address = self.socket.recvfrom(1024)
        except:
            gui.showToastBox("Port Closed")
            return False

        self.socket.settimeout(oldTimeout)

        if (self.ip, self.port) == address:
            self.__token = token.decode('utf-8')
            return True
        else:
            gui.showToastBox("Error server response, please try again")

    def user_login(self):
        msg = {
            "method": "LOGIN",
            "token": self.__token,
            "username": self.__username,
            "room": self.__room
        }

        msg = json.dumps(msg)
        msg = msg.encode('utf-8')

        self.socket.send(msg)

        resp, addr = self.socket.recvfrom(1024)

        resp = resp.decode('utf-8')

        if addr == (self.ip, self.port):
            if resp == "[SUCCESS]":
                return True
            elif resp == "[!USRUNAVL]":
                gui.showToastBox("Username unavailable")
                return False
        else:
            gui.showToastBox("Login failed, please try again")
            return False

    def send_usernameRoom(self, username, room):
        msg = {
            "method": "LOGIN",
            "token": self.__token,
            "username": username,
            "room": room
        }

        msg = json.dumps(msg).encode('utf-8')

        self.socket.send(msg)

    def send_msg(self, content):
        msg = {
            "method": "SEND",
            "token": self.__token,
            "username": self.__username,
            "msg": content
        }

        msg = json.dumps(msg).encode('utf-8')

        gui.addChatBox(msg, self.__username, True)
        self.socket.send(msg)

    def user_logout(self):
        msg = {
            "method": "LOGOUT",
            "token": self.__token,
            "username": self.__username,
        }

        msg = json.dumps(msg).encode('utf-8')

        self.socket.send(msg)

    def start_listen(self):
        worker = Worker(self.socket)
        self.threadpool.start(worker)


def check_connection(addr, port):
    msg = '{"method":"CONNECT"}'

    socket_test = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    socket_test.sendto(msg.encode('utf-8'), (addr, port))
    oldTimeout = socket_test.gettimeout()
    socket_test.settimeout(10)
    try:
        token, address = socket_test.recvfrom(1024)
    except:
        print("Port Closed")
        return False

    socket_test.settimeout(oldTimeout)

    if (addr, port) == address:
        return token.decode('utf-8')
    else:
        print("Error server response. Please try again")


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    client = Client()

    gui = GUI()
    engine.rootContext().setContextProperty("backend", gui)

    engine.load(os.path.join(os.path.dirname(__file__), "gui/connectHost.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
