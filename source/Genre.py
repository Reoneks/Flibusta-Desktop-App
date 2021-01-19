import tkinter as tk
from tkinter import Scrollbar
import requests
from bs4 import BeautifulSoup
import source.GenreBooks

class Example(tk.Toplevel):
 
    def __init__(self, master = None):
        super().__init__(master = master)
        self.init_UI()
 
    def init_UI(self):
        self.title("Жанры")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        Scroll = Scrollbar(self, orient=tk.VERTICAL)
        self.List = tk.Listbox(
            self,
            yscrollcommand = Scroll.set,
            height=20,
            width=100,
            font=("TkDefaultFont", 12)
        )
        self.List.bind("<<ListboxSelect>>", self.open_genre_books)
        Scroll.config(command = self.List.yview)
        Scroll.grid(sticky=tk.E+tk.N+tk.S, column = 1, row = 0, padx = 3, pady = 5)
        self.List.grid(sticky=tk.W+tk.E, column = 0, row = 0, padx = 3, pady = 5)
        self.parse()

    def parse(self):
        self.text = []
        self.anchor = []
        url = "http://flibusta.is/g"
        htmldata = requests.get(url)
        soup = BeautifulSoup(htmldata.content,'lxml')
        for i in soup.find('div', {'class': 'clear-block', 'id': 'main'}).find_all(['ul','h3']):
            if i.name == 'ul':
                for j in i.find_all('li'):
                    for k in j.find_all('a'):
                        if k.has_attr('href'):
                            if str(k['href']).find('/g/') != -1:
                                    if k['href'] not in self.anchor:
                                        self.text.append("    " + j.text.replace("\n",""))
                                        self.List.insert(tk.END,self.text[len(self.text)-1])
                                        self.anchor.append(k['href'])
            elif i.name == 'h3':
                self.List.insert(tk.END, i.text + ":")
                self.List.itemconfig("end", bg = "#b8af97")
    
    def open_genre_books(self, event):
        if self.List.curselection() != ():
            item = self.List.get(self.List.curselection())
            if item in self.text:
                index = self.text.index(item)
                app = source.GenreBooks.main("http://flibusta.is" + self.anchor[index], self.master)
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