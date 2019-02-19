from Tkinter import *

class Application(object):
    def createWidgets(self):
        self.main_frame.pack(fill=BOTH, expand=True)
        top_frame = Frame(self.main_frame, height=50, bg="black")
        top_frame.pack(side=TOP, fill=X)
        for i, tool in enumerate(self.tool_box):
            tool_label = Label(top_frame, text=tool, bg="black", fg="red")
            tool_label.pack(side=LEFT, fill=BOTH, expand=True)
        
        main_canvas = Frame(self.main_frame, height=300, bg="red")
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
        self.createWidgets()
        self.master.mainloop()

app = Application()