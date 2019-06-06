#!/usr/bin/python
import socket
from select import select

def connect(addr, username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.send("username {}\n\r".format(username))
    return sock

def main():
    IP   = '127.0.0.1'
    PORT = 8080
    username = 'shimi'
    sock = connect((IP, PORT), username)
    sock.send("chat start\n\r")
    print(sock.recv(1024))
    sock.close()

if __name__ == '__main__':
    main()
