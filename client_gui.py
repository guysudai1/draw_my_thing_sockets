from Tkinter import *
from functools import partial
import client
import time

        
class Application(object):
       
    def createWidgets(self):
        self.main_frame.pack(fill=BOTH, expand=True)
        canvas = Canvas(self.main_frame, bg="white")
        chat_canvas = Canvas(canvas, bg = "white", height=600, width=210,scrollregion=(0,0,10000,10000))
        chat_canvas.place(x=592,y=0)
        self.board_canvas = Canvas(canvas, bg = "white", height=600, width=116,scrollregion=(0,0,10000,10000))
        self.board_canvas.place(x=0,y=0)
        
        self.chat_text = Text(self.chat_canvas, height=35, width=25,bg="white",fg="black")
        self.chat_text.place(x=1,y=0)
        self.chat_text.config(state=DISABLED)

        self.board_text = Text(self.board_canvas, height=40, width=14,bg="white",fg="black")
        self.board_text.place(x=1,y=0)
        self.board_text.insert(END,"LEADER BOARD:\n\n")
        self.board_text.config(state=DISABLED)
        
        j=0
        for i, tool in enumerate(self.tool_box):
            tool_button = Button(canvas, width=31, height=2, bg="black",fg="white",text=tool,command = partial(self.command_color, "white"))
            tool_button.place(x=225*j+130, y=2)
            j += 1
            
        j = 0    
        for i, color in enumerate(self.colors):
            color_button = Button(canvas, bg=color, fg="red", command = partial(self.command_color, color),width=5)
            color_button.place(x=45*j+130,y=572)
            j+=1
            
        self.chat_entry = Entry(chat_canvas, bd =5)
        self.chat_entry.place(x=1,y=570)
        self.master.bind('<Return>',self.send_message)
        
        
        line1 = canvas.create_rectangle(120,0,130,600,fill="black") 
        line2 = canvas.create_rectangle(580,0,590,600,fill="black")

        
        canvas.pack(fill=BOTH, expand=1)
    
    def send_message(self,event):
        msg = self.chat_entry.get()
        client.send_chat_message(msg)
        self.chat_entry.delete(0, 'end')
        
    def writing_chat(self):
        msg = self.cls.get_command().strip("\n\r")
        new_msg = msg.replace("_"," ")
        for i in range(4):
            is_chat += new_msg[i]

        if(is_chat == "chat"):    
            self.chat_text.config(state=NORMAL)
            self.chat_text.insert(END,new_msg+"\n")
            self.chat_text.config(state=DISABLED)
        
    def writing_board(self):
        msg = self.cls.get_command().strip("\n\r")
        is_get_p = ""
        for i in range(10):
            is_get_p += msg[i]
            
        if(is_get_p == "getplayers"):    
            self.board_text.config(state=NORMAL)
            split_msg = msg.split()
            for i in range(1,len(split_msg)):
                split_newmsg = split_msg[i].split(',',1)
                self.board_text.insert(END,split_newmsg[0] + ": " +  split_newmsg[1] + "\n")
            self.board_text.config(state=DISABLED)
        
    def destroy_master(self):
        self.master.destroy()
           
    def init_master(self):
        self.master.title('Draw My Thing v1')
        self.master.geometry("800x600")
        self.master.resizable(0,0)
        
    def __init__(self):
        self.cls = client.Classy(raw_input("Username: "))
        self.master = Tk()
        self.init_master()
        self.main_frame = Frame(self.master, bg="white")
        self.tool_box = ["pen", "eraser"]
        self.colors = ["black", "red", "blue", "orange", "green", "yellow" , "pink", "purple", "brown", "grey"]
        self.mouse_color = ""
        self.hexcolor = "FFFFFF"
        self.command_color(self.mouse_color)
        self.createWidgets()
        self.writing_chat()
        self.writing_board()
        #self.master.bind('<B1-Motion>',self.motion)
        self.master.mainloop()

app = Application()
