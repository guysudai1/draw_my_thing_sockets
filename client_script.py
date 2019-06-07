#!/usr/bin/python
import socket
from select import select
from threading import Thread
from sys import exit

def connect(addr, username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.send("username {}\n\r".format(username))
    return sock

def get_messages(sock): 
    while True:
        rd, _, _ = select([sock], [], [])
        for i in rd:
            data = i.recv(1024)
            if data:
                print(data)
            else:
                sock.close()
                exit(1)
def main():
    IP   = '127.0.0.1'
    PORT = 8080
    username = 'shimon'
    sock = connect((IP, PORT), username)
    t = Thread(target=get_messages, args=(sock, ))
    t.start()
    while True:
        print("Message:")
        inp = raw_input()
        if inp == "!":
            break
        sock.send("{}\n\r".format(inp))
    sock.close()
    exit(1)

if __name__ == '__main__':
    main()
