import socket, select, signal, sys, threading, time, re
import os


threads = []

class Classy(object):
    def __init__(self, username):
        self.got_image = False
        self.sock = socket.socket()
        self.sock.connect(('', 8080))
        self.sock.send("username " + username + "\n\r")
	t = threading.Thread(target=self.recv_image)
	t.start()

    def send_mouse_cor(self, cord_list):
        coordinate_length = 15 # 000,000,000000 <- space
        message_max_length = 2048
        length_of_string = len(cord_list) * coordinate_length - 1
        while (length_of_string > message_max_length):
            place_in_list = int(message_max_length / coordinate_length) - 1
            string_to_send = " ".join(cord_list[:place_in_list])
            self.sock.send("canvas_change {}\n\r".format(string_to_send))
            send_cord_list = cord_list[place_in_list:]
            length_of_string = len(cord_list) * coordinate_length - 1

        string_to_send = " ".join(cord_list)
        self.sock.send("canvas_change {}\n\r".format(string_to_send))
    def get_command(self):
	cmd = ""
	end = "\n\r"
	hit = 0
	while (hit < len(end)):
		letter = self.sock.recv(1)
		cmd += letter
		if (letter == end[hit]):
			hit += 1
		else:
			hit = 0
	return cmd

    def recv_image(self):
        while True:
	    msg = self.get_command().strip("\n\r")
            canvas_change_regex = r"^canvas_change [0-9]{1,5} png [0-9]{1,10}$"
            if (re.match(canvas_change_regex, msg)):
                    msg = msg.split(" ")	
                    block_count, file_format, block_size = int(msg[1]), msg[2], int(msg[3])
                    canvas = ""
		    i = 0
                    while i < block_count:
                            cur_msg = self.get_command().strip("\n\r")
                            if (cur_msg.startswith("IMG ")):
                                canvas += cur_msg[4:]
				i += 1
                    with open("canvas.png", "w") as f:
                        f.write(canvas)
                    self.got_image = True

        """
        info = sock.recv(1024)# block_count , file_format, block_size
        sock.send("RECV")
        
        info = info.split(' ')
        block_count, file_format, block_size = info[0], info[1], info[2]
        data = ""
        
        for i in range(block_count):
            data += block_size
        
        with open("canvas" + file_format, "wb") as image:
            image.write(data)
        """

