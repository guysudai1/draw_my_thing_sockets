import socket, select, signal, sys, threading
import os

sock = socket.socket()
threads = []
def main():
    global sock
    SERVER_INFO = ("127.0.0.1", 8080)
    sock.connect(SERVER_INFO)
    signal.signal(signal.SIGINT, handler)
    mainloop(sock)
    sock.close()

def handler(signum, frame):
    global sock
    print("Closing socket...")
    sock.close()
    sys.exit(0)

def get_input(socket):
    while True:
        rd, _, _ = select.select([socket], [], [])        
        for r in rd:
            data = r.recv(1024)
            if data:
                print("Received: {}".format(data))
            else:
                socket.close()
                break
    

def mainloop(sock):
    thread1 = threading.Thread(target=get_input, args=(sock, ))
    thread1.start()
    threads.append(thread1)
    while True:
        inp = raw_input("Chat input: ")
        sock.send("chat {}".format(inp))
 
def wait_for_image(sock):
    while True:
        rd, wr, er = select.select([sock], [], [])
        for socket in rd:
            info = socket.recv(1024)
            if (info.startswith("SIZE")):
                print("Receiving Image")
                sock.send("RECV")
                _, times, ext, message_size = info.split(' ')
                file_recv = ""
                for i in range(int(times)):
                    file_recv += socket.recv(int(message_size))
                    
                file_name = os.getcwd() + "\\recvCanvas" + ext
                with open(file_name, "wb") as f:
                    f.write(file_recv)
            elif info != "":
                print(info)
                            
if __name__ == "__main__":
    main()