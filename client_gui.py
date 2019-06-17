from Tkinter import *
from functools import partial
import client
import time

        
class Application(object):
    def command_color(self,color):
        self.hexcolor = "FFFFFF"
        if color == "black":
            self.hexcolor = "000000"
        elif color == "red":
            self.hexcolor = "FF0000"
        elif color == "blue":
            self.hexcolor = "0000FF"
        elif color == "green":
            self.hexcolor = "00FF00"
        elif color == "yellow":
            self.hexcolor = "FFFF00"
        elif color == "orange":
            self.hexcolor = "D35400"
        elif color == "grey":
            self.hexcolor = "ABB2B9"
        elif color == "pink":
            self.hexcolor = "FFC0CB"
        elif color == "purple":
            self.hexcolor = "8E44AD"
        elif color == "white":
            self.hexcolor = "FFFFFF"
        
    def createWidgets(self):
        self.main_frame.pack(fill=BOTH, expand=True)
        canvas = Canvas(self.main_frame, bg="white")
        chat_canvas = Canvas(canvas, bg = "white", height=600, width=210,scrollregion=(0,0,10000,10000))
        chat_canvas.place(x=592,y=0)

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
        self.master.bind('<Return>',self.writing)
        
        
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
        
    def destroy_master(self):
        self.master.destroy()
           
    def init_master(self):
        self.master.title('Draw My Thing v1')
        self.master.geometry("800x600")
        self.master.resizable(0,0)
        
    def __init__(self):
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
        #self.master.bind('<B1-Motion>',self.motion)
        self.master.mainloop()

app = Application()
