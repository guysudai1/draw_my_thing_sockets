from Tkinter import *

def command1(color):
        mouse_color = color
        
class Application(object):
    def createWidgets(self):
        self.main_frame.pack(fill=BOTH, expand=True)
        top_frame = Frame(self.main_frame, height=50, bg="black")
        top_frame.pack(side=TOP, fill=X)
        bottom_frame = Frame(self.main_frame, height=50)
        bottom_frame.pack(side=BOTTOM, fill=X)
        for i, tool in enumerate(self.tool_box):
            tool_label = Button(top_frame, text=tool, bg="black", fg="red", command = command1("white"))
            tool_label.pack(side=LEFT, fill=BOTH, expand=True)
        for i, color in enumerate(self.colors):
            color_button = Button(bottom_frame, bg=color, fg="red", command = command1(color))
            color_button.pack(side=LEFT, fill=BOTH, expand=True)
        
        main_canvas = Frame(self.main_frame, height=300, bg="white")
        main_canvas.pack(side=TOP, fill=X)
        

        
    def destroy_master(self):
        self.master.destroy()
           
    def init_master(self):
        self.master.title('Draw My Thing v1')
        self.master.geometry("500x500")
        self.master.resizable(0,0)
        
    def __init__(self):
        self.master = Tk()
        self.init_master()
        self.main_frame = Frame(self.master, bg="white")
        self.tool_box = ["pen", "eraser"]
        self.colors = ["black", "red", "blue", "orange", "green", "yellow" , "pink", "purple", "brown", "grey"]
        self.createWidgets()
        self.master.mainloop()

app = Application()
