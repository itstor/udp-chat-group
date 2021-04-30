import sys
import json
import socket


class Client:
    def __init__(self, ip, port, token):
        self.ip = ip
        self.port = int(port)
        self.__token = token
        self.__username = ""
        self.__room = ""
        self.running = True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((self.ip, self.port))

    def start(self):
        if (self.user_login()):
            self.listen()

    def user_login(self):
        while True:
            self.__username = input("Input Username: ")
            self.__room = input("Join Room: ")

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
                    print("Username sudah digunakan")
                    continue
            else:
                print("Login gagal silahkan coba lagi")
                continue

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

        self.socket.send(msg)

    def user_logout(self):
        msg = {
            "method": "LOGOUT",
            "token": self.__token,
            "username": self.__username,
        }

        msg = json.dumps(msg).encode('utf-8')

        self.socket.send(msg)

        sys.exit()

    def listen(self):
        msgformat = {"method": "SEND",
                     "token": self.__token,
                     "username": self.__username
                     }

        self.socket.settimeout(1)

        while self.running:
            try:
                msg = input(f"{self.__username} > ")
                if msg != "":
                    sendmsg = msgformat
                    sendmsg["msg"] = f"{self.__username} > " + msg
                    sendmsg = json.dumps(sendmsg).encode('utf-8')
                    self.socket.send(sendmsg)

                data = self.socket.recv(1024)
                data = data.decode('utf-8')
                print(data)

            except KeyboardInterrupt:
                self.user_logout()
            except:
                pass


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
    token = ""

    while not token:
        ip = input("Input Host IP: ")
        try:
            port = int(input("Input Host Port: "))
        except ValueError:
            print("Input hanya angka")
            continue
        token = check_connection(ip, port)

    client = Client(ip, port, token)
    client.start()
