import tkinter as tk
from tkinter import ttk
import sqlite3
from io import BytesIO
from PIL import ImageTk, Image
from tkinter.scrolledtext import ScrolledText
import source.BookInfo

class Example(tk.Toplevel):
 
    def __init__(self, master = None):
        super().__init__(master = master)
        self.init_UI()
        self.fill_notebook()

    def init_UI(self):
        self.title("Библиотека")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.Library_Types = ttk.Notebook(self)
        self.Library_Types.bind('<<NotebookTabChanged>>', self.set_text)
        self.Library_Types.grid(column=0, row=0)
    
    def fill_notebook(self):
        conn = sqlite3.connect('./database/books.sqlite')
        c = conn.cursor()
        c.execute("SELECT [Type name] FROM [Library types]")
        data = c.fetchall()
        self.tabs = []
        for j in [i[0] for i in data]:
            self.tabs.append(ttk.Frame(self.Library_Types))
            self.Library_Types.add(self.tabs[len(self.tabs) - 1], text=j)
        conn.close()
    
    def set_text(self, event = None):
        for widget in self.tabs[self.Library_Types.index(self.Library_Types.select())].winfo_children():
            widget.destroy()
        name = self.Library_Types.tab(self.Library_Types.select(), "text")
        self.list_box = ScrolledText(self.tabs[self.Library_Types.index(self.Library_Types.select())])
        self.list_box.pack(side="top", fill="both", expand=True)
        conn = sqlite3.connect('./database/books.sqlite')
        c = conn.cursor()
        c.execute("SELECT rowid FROM [Library types] WHERE [Type name] = ?", (name,))
        data = c.fetchone()[0]
        self.frames = []
        self.images = []
        for i in c.execute("SELECT * FROM [Library] WHERE Type = ?", (data,)):
            self.frames.append(tk.Frame(self.list_box))
            self.frames[len(self.frames)-1].bind('<Button-1>',self.open_book_info)
            self.images.append(ImageTk.PhotoImage(Image.open(BytesIO(i[0])).resize((50,60))))
            label = tk.Label(self.frames[len(self.frames)-1], image = self.images[len(self.images)-1])
            label.myId = "1"
            label.pack()
            label1 = tk.Label(self.frames[len(self.frames)-1], text = i[2])
            label1.myId = "2"
            label1.pack()
            label2 = tk.Label(self.frames[len(self.frames)-1], text = i[3])
            label2.myId = "3"
            label2.pack()
            label3 = tk.Label(self.frames[len(self.frames)-1], text = i[4])
            label3.myId = "4"
            label3.pack()
            label4 = tk.Label(self.frames[len(self.frames)-1], text = i[5])
            label4.myId = "5"
            label4.pack()
            label5 = tk.Label(self.frames[len(self.frames)-1], text = "    " + i[7], wraplength=640, justify="left")
            label5.myId = "6"
            label5.pack()
            label6 = tk.Label(self.frames[len(self.frames)-1], text = i[6])
            label6.myId = "7"
            label6.pack()
            label7 = tk.Label(self.frames[len(self.frames)-1], text = i[8])
            label7.myId = "8"
            label7.pack()
            label8 = tk.Label(self.frames[len(self.frames)-1], text = i[1])
            label8.myId = "url"
            label8.pack()
            self.list_box.window_create(tk.END, window = self.frames[len(self.frames)-1])
            self.list_box.insert(tk.END, '\n\n')

    def open_book_info(self, event):
        app = source.BookInfo.main([i['text'] for i in event.widget.winfo_children() if i.myId == "url"][0], self.master)
        app.bind("<<Close>>", self.on_close_app, '+')
        self.withdraw()
    
    def on_closing(self):
        self.event_generate("<<Close>>")
        self.destroy()
        
    def on_close_app(self, event):
        self.deiconify()

def main(master):
    app = Example(master)
    return app