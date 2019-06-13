from Tkinter import *
from functools import partial
import client
import time


def command_color(color):
        mouse_color = color
        print mouse_color
        
class Application(object):
    def createWidgets(self):
        self.main_frame.pack(fill=BOTH, expand=True)
        canvas = Canvas(self.main_frame, bg="white", height=800, width=600)
        j=0
        for i, tool in enumerate(self.tool_box):
            tool_button = Button(canvas, width=31, height=2, bg="black",fg="white",text=tool,command = partial(command_color, "white"))
            tool_button.place(x=225*j+130, y=0)
            j += 1
            
        j = 0    
        for i, color in enumerate(self.colors):
            color_button = Button(canvas, bg=color, fg="red", command = partial(command_color, color),width=5)
            color_button.place(x=45*j+130,y=572)
            j+=1
            
        chat_entry = Entry(canvas, bd =5,)
        chat_entry.place(x=591,y=570)
        send_button = Button(canvas, bg = "black", fg="white", text="send",height=1,width=8)
        send_button.place(x=725,y=570)

        line1 = canvas.create_rectangle(120,0,130,600,fill="black") 
        line2 = canvas.create_rectangle(580,0,590,600,fill="black")

        
        canvas.pack(fill=BOTH, expand=1)
        
    
    def motion(self,event):
        x, y = event.x, event.y
        if(x >= 0 and x<=800 and y >= 0 and y<=623):
            client.send_mouse_cor(x,y)
            time.sleep(0.1);
        
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
        self.createWidgets()
        self.master.bind('<B1-Motion>',self.motion)
        self.master.mainloop()

app = Application()
