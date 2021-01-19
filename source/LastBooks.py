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
        self.title("Последние поступления")
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
        self.parse()
    
    def get_books(self,url):
        htmldata = requests.get(url)
        soup = BeautifulSoup(htmldata.content,'lxml')
        for i in soup.find('div', {'class': 'clear-block', 'id': 'main'}).select('div.clear-block > div'):
            its_a_book = False
            if i.find('p', {'class': 'genre'}) != None:
                its_a_book = True
                self.List.insert(tk.END, i.find('p', {'class': 'genre'}).text + ":")
                self.List.itemconfig("end", bg = "#b8af97")
            for j in i.find_all('a'):
                if len(str(j['href']).split("/")) == 3 and str(j['href']).find('/b/') != -1:
                    if j['href'] not in self.anchor:
                        self.text.append("    " + j.text.replace("\n",""))
                        self.anchor.append(j['href'])
                elif len(str(j['href']).split("/")) == 3 and str(j['href']).find('/a/') != -1 and len(self.text) > 0:
                    self.text[-1] += " - " + j.text.replace("\n","")
            if len(self.text) > 0 and its_a_book:
                self.List.insert(tk.END,self.text[len(self.text)-1])

    def parse(self):
        self.text = []
        self.anchor = []
        self.get_books("http://flibusta.is/new")
        self.get_books("http://flibusta.is/new?page=1")
    
    def open_book_info(self, event):
        if self.List.curselection() != ():
            item = self.List.get(self.List.curselection())
            index = self.text.index(item)
            app = source.BookInfo.main("http://flibusta.is" + self.anchor[index], self.master)
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