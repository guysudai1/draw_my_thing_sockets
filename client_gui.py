from Tkinter import *
from tkColorChooser import askcolor
#from Tkinter import tkColorChooser 
from PIL import Image, ImageDraw, ImageFile, ImageTk
from functools import partial
from threading import Timer, Thread
import client
import time
        
class Application(object):
    def createWidgets(self):
        self.main_frame.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(self.main_frame, bg="white", height=600, width=900)
        #for i, tool in enumerate(self.tool_box):
        #    tool_button = Button(self.canvas, width=15, height=2, bg="black",fg="white",text=tool)
        #    tool_button.place(x=225*i+130, y=0)
        pen_tool = Button(self.canvas, width=22, height=2, bg="black", fg="white", text="PEN", command=partial(self.replace_tool, "pen"))
        pen_tool.place(x=160, y=0)
        eraser_tool = Button(self.canvas, width=22, height=2, bg="black", fg="white", text="ERASER", command=partial(self.replace_tool, "eraser"))
        eraser_tool.place(x=355, y=0)
	self.chat_canvas = Canvas(self.canvas, bg = "white", height=600, width=330,scrollregion=(0,0,10000,10000))
        self.chat_canvas.place(x=570,y=0)
        self.board_canvas = Canvas(self.canvas, bg = "white", height=600, width=150,scrollregion=(0,0,10000,10000))
        self.board_canvas.place(x=0,y=0)
            
	self.chat_text = Text(self.chat_canvas, height=33, width=39,bg="white",fg="black")
        self.chat_text.place(x=7,y=0)
        self.chat_text.config(state=DISABLED)
	
	self.board_text = Text(self.board_canvas, height=40, width=20,bg="white",fg="black")
        self.board_text.place(x=1,y=0)
        self.board_text.insert(END,"LEADERBOARD:\n\n")
        self.board_text.config(state=DISABLED)
        """
        j = 0    
        for i, color in enumerate(self.colors):
            color_button = Button(canvas, bg=color, fg="red", command = partial(command_color, color),width=5)
            color_button.place(x=45*j+130,y=522)
            j+=1
        """
        #self.send_button = Button(self.canvas, bg = "black", fg="white", text="send",height=1,width=8)
        #self.send_button.place(x=725,y=570)
        
        self.chat_entry = Entry(self.chat_canvas, bd=4, width=38)
        self.chat_entry.place(x=6,y=570)
        self.master.bind('<Return>',self.send_message)
       

        self.ability_canvas = Canvas(self.canvas, bg="white", height=100, width=400)
        self.ability_canvas.place(x=160, y=450)
        
        self.blindteam_button = Button(self.ability_canvas,bg="black",fg="white",text="Blind\nTeam\n5",width = 3, height=3, command = partial(self.cls.send_ability,"blindteam",""))
        self.blindteam_button.place(x=10,y=20)

        self.blindperson_button = Button(self.ability_canvas,bg="black",fg="white",text = "Blind\nPerson\n3",width=3, height=3, command=self.player_name_window)
        self.blindperson_button.place(x=65,y=20)

        

        self.word_canvas = Canvas(self.canvas, bg="white", height=50, width=400)
        self.word_canvas.place(x=159, y=450+100)
        self.word = Text(self.word_canvas, height=50, width= 400, bg="white", fg="black", font=('Arial', 20))
        self.word.place(x=0,y=0)
        self.word.config(state=DISABLED)

        line1 = self.canvas.create_rectangle(150,0,160,600,fill="black") 
        line2 = self.canvas.create_rectangle(560,0,570,600,fill="black")


        self.image_canvas = Canvas(self.canvas, bg="white", height=400, width=400)
        self.image_canvas.place(x=160, y=50)
        self.lastx = self.lasty = None
        self.image_canvas.bind('<1>', self.paint_image)
     
        self.get_color_button = Button(self.canvas, bg="black", fg="white", text="Choose Color", height=3, width=15, command=self.select_color)
        self.get_color_button.place(x=3,y=600-66)
    
        t = Thread(target=self.get_messages)
        t.start()

        self.canvas.pack()

    def replace_tool(self, tool):
        if (tool == "pen"):
            self.eraser = False
        if (tool == "eraser"):
            self.eraser = True
        return

    def send_message(self, event):
        msg = self.chat_entry.get()
        self.cls.send_chat_message(msg)
        self.chat_entry.delete(0, 'end') 
        self.chat_text.config(state=NORMAL)
        self.chat_text.insert(END, "You: " + msg + "\n")
        self.chat_text.config(state=DISABLED)

    def get_messages(self):
        while True:
            # TODO : Add canvas thing here with cords(or IN gui)
            message = self.cls.get_command().strip("\n\r")
            split_data = message.split(' ')
            canvas_change_regex = r"^canvas_change [a-z0-9]{6} [0-9]{1,2} ([0-9]{1,3},[0-9]{1,3} )+$"
	    chat_regex 			 = r"^chat [a-zA-Z0-9.,?:_]{1,150}$"
	    get_players			 = r"^getplayers ([a-z0-9]{1,20},[0-9]{1,10} )+$"
            word_regex                   = r"^word ([0-9]{1,2}_)+$"
            #print("Message: " + message)
            if re.match(canvas_change_regex, message + " "):
                self.update_image(split_data[1], int(split_data[2]), split_data[3:])
	    elif re.match(chat_regex, message):
		message = message.replace("_", " ")
		self.chat_text.config(state=NORMAL)
                self.chat_text.insert(END, message[5:] + "\n")
            	self.chat_text.config(state=DISABLED)

    	    elif re.match(get_players, message + " "):
 		self.board_text.config(state=NORMAL)
	    	split_msg = message.split(" ")[1:]
    		self.board_text.delete(1.0, END)
                self.board_text.insert(END, "LEADERBOARD:\n\n")
                for player_score in split_msg:
        		split_player_score = player_score.split(',')
	        	self.board_text.insert(END,split_player_score[0] + ": " +  split_player_score[1] + "\n")
		self.board_text.config(state=DISABLED)
            elif re.match(word_regex, message + "_"):
                message = message.split(" ")[1]
                word = ""
                for i in message.split("_"):
                    word += int(i) * "_ "
                    word += " "
                #print("WORD: " + word)
                self.word.config(state=NORMAL)
                self.word.delete(1.0, END)
                self.word.insert(END, "WORD: " + word)
                self.word.config(state=DISABLED)
            elif (message == "resetboard"):
                self.image_canvas.delete("all") 
        


    def update_image(self, color, width, cord_array):
        cord_array = [tuple(x.split(',')) for x in cord_array]
        tuple_to_int_tuple = lambda x: tuple([int(i) for i in x])
        cord_array = [tuple_to_int_tuple(x) for x in cord_array]
        if len(cord_array) == 1:
            return
        for i, cord in enumerate(cord_array[:-1]):
            next_cord = cord_array[i+1]
            self.image_canvas.create_line(cord[0], cord[1], next_cord[0], next_cord[1], fill="#{}".format(color), width=width)
        """ 
        self.color_canvas = Canvas(canvas, bg="white", height=128, width=128)
        self.color_canvas.place(y=600-128, x=0)
        self.color_canvas.bind('<1>', self.change_red_green)
        self.load_colorpicker()

        self.color_canvas_third = Canvas(canvas, bg="white", height=128, width=150 - 130)
        self.color_canvas_third.place(y=600-128, x=128)
        for i in range(0, 256, 2):
            colorhex = "#%02x%02x%02x" % (0, 0, i)
            self.color_canvas_third.create_rectangle(0, i,150 - 130, i+1, outline=colorhex) 
        self.color_canvas_third.bind("<1>", self.change_blue)
    """
        
    """
    def load_colorpicker(self):
        blue = self.color[2]
        for red in range(0,256):
            for green in range(0,256):
                colorhex = "#%02x%02x%02x" % (red, green, blue)
                self.color_canvas.create_rectangle(red, green, red + 1, green + 1, outline=colorhex)

    def change_red_green(self, event):
        self.color = (event.x, event.y, self.color[2])
        
    def change_blue(self, event):
        self.color = (self.color[0], self.color[1], event.y)
        self.load_colorpicker()
    """
    def player_name_window(self): # new window definition
        self.new_win = Toplevel(self.master)
        self.p_name = Entry(self.new_win)
        self.new_win.bind('<Return>',self.send_blind_person)
        self.p_name.pack()
          
    def send_blind_person(self, event):
        msg = self.p_name.get()
        self.cls.send_ability("blindperson", msg)
        self.new_win.destroy() 
    
    def select_width(self):
        print("hey")

    def paint_image(self, event):
        self.lastx, self.lasty = event.x, event.y
        self.image_canvas.bind('<B1-Motion>', self.do_painting)
        #print(event.x, event.y)

    def get_drawn_pixels(self, color, cord_list, width=1):
        if len(cord_list) > 0:
            self.cls.send_mouse_cor(color, cord_list, width)
        
    def do_painting(self, event):
        x, y = event.x, event.y
        #self.image_canvas.create_line((self.lastx, self.lasty, x, y), fill=self.color, width=1)
        if (not self.timer.is_alive()):
            self.drawn_pixels = []
            if self.eraser == True:
                self.timer = Timer(self.time_refresh, self.get_drawn_pixels, ["ffffff", self.drawn_pixels, 20])
            else:
                self.timer = Timer(self.time_refresh, self.get_drawn_pixels, [self.color[1:], self.drawn_pixels, 2])
            self.timer.start()
        #self.draw.line((self.lastx, self.lasty, x, y), fill=self.color, width=1)
        self.lastx, self.lasty = x, y
        if ((x >= 0 and y >= 0) and (x < 400 and y < 400)):
            self.drawn_pixels.append("{},{}".format(x,y))

    def destroy_master(self):
        self.master.destroy()
    
    def select_color(self):
        color = askcolor()
        self.color = color[1]
        

    def init_master(self):
        self.master.title('Draw My Thing v1')
        self.master.geometry("900x600")
        self.master.resizable(0,0)
        
    def __init__(self):
        self.cls = client.Classy(raw_input("Username: "))
        self.master = Tk()
        self.init_master()
        self.main_frame = Frame(self.master, bg="white")
        self.tool_box = ["pen", "eraser"]
        self.drawn_pixels = []
        self.time_refresh = 0.1
        self.eraser = False
        self.color = "#000000" # BLACK
        self.timer = Timer(self.time_refresh, self.get_drawn_pixels, [self.drawn_pixels])
        self.createWidgets()
        #self.master.bind('<B1-Motion>',self.motion)
        self.master.mainloop()

app = Application()
