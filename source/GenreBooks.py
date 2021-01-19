import tkinter as tk
from tkinter import Scrollbar
import requests
from bs4 import BeautifulSoup
import source.BookInfo

class Example(tk.Toplevel):
 
    def __init__(self, master = None):
        super().__init__(master = master)
        self.init_UI()
 
    def init_UI(self):
        self.title("Книги по жанру")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        Scroll = Scrollbar(self, orient=tk.VERTICAL)
        self.List = tk.Listbox(
            self,
            yscrollcommand = Scroll.set,
            height=20,
            width=100,
            font=("TkDefaultFont", 12)
        )
        self.List.bind("<<ListboxSelect>>", self.open_book_info)
        Scroll.config(command = self.List.yview)
        Scroll.grid(sticky=tk.E+tk.N+tk.S, column = 1, row = 0, padx = 3, pady = 5)
        self.List.grid(sticky=tk.W+tk.E, column = 0, row = 0, padx = 3, pady = 5)

    def parse(self, url):
        self.text = []
        self.anchor = []
        number = 1
        htmldata = requests.get(url)
        soup = BeautifulSoup(htmldata.content,'lxml')
        for i in soup.find('div', {'class': 'clear-block', 'id': 'main'}).find('ol').find_all(['a','h5']):
            if i.name == 'a':
                if len(str(i['href']).split("/")) == 3 and str(i['href']).find('/b/') != -1:
                    if i['href'] not in self.anchor:
                        self.text.append("    " + str(number) + ". " + i.text.replace("\n",""))
                        self.List.insert(tk.END,self.text[len(self.text)-1])
                        self.anchor.append(i['href'])
                        number += 1
            elif i.name == 'h5':
                self.List.insert(tk.END, i.text + ":")
                self.List.itemconfig("end", bg = "#b8af97")
    
    def open_book_info(self, event):
        if self.List.curselection() != ():
            item = self.List.get(self.List.curselection())
            if item in self.text:
                index = self.text.index(item)
                app = source.BookInfo.main("http://flibusta.is" + self.anchor[index], self.master)
                app.bind("<<Close>>", self.on_close_app, '+')
                self.withdraw()
    
    def on_closing(self):
        self.event_generate("<<Close>>")
        self.destroy()
        
    def on_close_app(self, event):
        self.deiconify()

def main(url, master):
    app = Example(master)
    app.parse(url)
    return app