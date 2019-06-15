from Tkinter import *
from tkColorChooser import askcolor
#from Tkinter import tkColorChooser 
from PIL import Image, ImageDraw, ImageFile, ImageTk
from functools import partial
from threading import Timer, Thread
import client
import time
ImageFile.LOAD_TRUNCATED_IMAGES = True
        
class Application(object):
    def createWidgets(self):
        self.main_frame.pack(fill=BOTH, expand=True)
        canvas = Canvas(self.main_frame, bg="white", height=600, width=800)
        for i, tool in enumerate(self.tool_box):
            tool_button = Button(canvas, width=15, height=2, bg="black",fg="white",text=tool)
            tool_button.place(x=225*i+130, y=0)
            
            
        """
        j = 0    
        for i, color in enumerate(self.colors):
            color_button = Button(canvas, bg=color, fg="red", command = partial(command_color, color),width=5)
            color_button.place(x=45*j+130,y=522)
            j+=1
        """
        chat_entry = Entry(canvas, bd=5)
        chat_entry.place(x=591,y=570)
        send_button = Button(canvas, bg = "black", fg="white", text="send",height=1,width=8)
        send_button.place(x=725,y=570)
        
       
        line1 = canvas.create_rectangle(150,0,160,600,fill="black") 
        line2 = canvas.create_rectangle(560,0,570,600,fill="black")


        self.image_canvas = Canvas(canvas, bg="white", height=400, width=400)
        self.image_canvas.place(x=160, y=50)
        image        = Image.new("RGB", (400,400), 'white')
        self.draw    = ImageDraw.Draw(image)
        self.lastx = self.lasty = None
        self.image_canvas.bind('<1>', self.paint_image)
    
        self.get_color_button = Button(canvas, bg="black", fg="white", text="Choose color", height=1, width=8, command=self.select_color)
        self.get_color_button.place(x=0,y=600-25)
    
        t = Thread(target=self.update_image)
        t.start()
        canvas.pack()

    def update_image(self):
        while True:
            if self.cls.got_image:
                time.sleep(0.2)
                image = Image.open("canvas.png")
                image = ImageTk.PhotoImage(image)
                image_sprite = self.image_canvas.create_image(200,200, image=image)
                self.cls.got_image = False
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
    def paint_image(self, event):
        self.lastx, self.lasty = event.x, event.y
        self.image_canvas.bind('<B1-Motion>', self.do_painting)
        print(event.x, event.y)

    def get_drawn_pixels(self, cord_list):
        if len(cord_list) > 0:
            self.cls.send_mouse_cor(cord_list)
        
    def do_painting(self, event):
        x, y = event.x, event.y
        #self.image_canvas.create_line((self.lastx, self.lasty, x, y), fill=self.color, width=1)
        if (not self.timer.is_alive()):
            self.drawn_pixels = []
            self.timer = Timer(0.25, self.get_drawn_pixels, [self.drawn_pixels])
            self.timer.start()
        #self.draw.line((self.lastx, self.lasty, x, y), fill=self.color, width=1)
        self.lastx, self.lasty = x, y
        if ((x >= 0 and y >= 0) and (x < 400 and y < 400)):
            self.drawn_pixels.append("{},{},{}".format(x,y,self.color[1:]))

    def destroy_master(self):
        self.master.destroy()
    
    def select_color(self):
        color = askcolor()
        self.color = color[1]
        print(self.color)

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
        self.drawn_pixels = []
        self.color = "#000000" # BLACK
        self.timer = Timer(0.25, self.get_drawn_pixels, [self.drawn_pixels])
        self.createWidgets()
        #self.master.bind('<B1-Motion>',self.motion)
        self.master.mainloop()

app = Application()
