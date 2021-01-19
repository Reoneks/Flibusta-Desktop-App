import tkinter as tk
from tkinter import Scrollbar
import requests
from bs4 import BeautifulSoup
import source.BookInfo
import source.Sequence
import source.OpenAuthorInfo

class Example(tk.Toplevel):
 
    def __init__(self, master = None):
        super().__init__(master = master)
        self.init_UI()
 
    def init_UI(self):
        self.title("Поиск книги")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        for i in range(4):
            self.columnconfigure(i, weight=1)
        for i in range(3):
            self.rowconfigure(i, weight=1)
        Text = tk.Label(
            self,
            text="Введите название книги/серии/автора:",
            font=("Times New Roman",12)
        )
        Text1 = tk.Label(
            self,
            text="Результат поиска:",
            font=("Times New Roman",12)
        )
        self.Line = tk.Entry(
            self,
            font=("Times New Roman",12)
        )
        Find = tk.Button(
            self,
            text="Найти",
            font=("Times New Roman",12),
            command=self.parse
        )
        Scroll = Scrollbar(self, orient=tk.VERTICAL)
        self.List = tk.Listbox(
            self,
            yscrollcommand = Scroll.set,
            font=("TkDefaultFont", 12)
        )
        self.Line.bind('<Return>', self.redirect_to_parse)
        self.List.bind("<<ListboxSelect>>", self.open_book_info)
        Scroll.config(command = self.List.yview)
        Text.grid(sticky=tk.W, column = 0, row = 0)
        self.Line.grid(sticky=tk.W+tk.E, column = 1, row = 0, padx = 3)
        Find.grid(column = 2, row = 0)
        Text1.grid(sticky=tk.W, column = 0, row = 1)
        Scroll.grid(sticky=tk.E+tk.N+tk.S, column = 3, row = 2, padx = 3, pady = 5)
        self.List.grid(sticky=tk.W+tk.E, column = 0, row = 2, columnspan=3, padx = 3, pady = 5)
    
    def redirect_to_parse(self, event):
        self.parse()

    def parse(self):
        self.List.delete(0, tk.END)
        self.text = []
        self.anchor = []
        url = "http://flibusta.is/booksearch?ask=" + self.Line.get().replace(" ","+")
        self.Line.delete(0, tk.END)
        while url != "":
            url = self.parse_page(url)
    
    def parse_page(self, url):
        htmldata = requests.get(url)
        soup = BeautifulSoup(htmldata.content,'lxml')
        for i in soup.find('div', {'class': 'clear-block', 'id': 'main'}).select('div.clear-block > ul,h3'):
            if i.name == "ul":
                for j in i.find_all('li'):
                    self.text.append("    " + j.text.replace("\n",""))
                    self.List.insert(tk.END,self.text[len(self.text)-1])
                    self.anchor.append(j.find('a')['href'])
            else:
                self.List.insert(tk.END, ' '.join(i.text.split()))
                self.List.itemconfig("end", bg = "#b8af97")
        if soup.find('li', {'class': 'pager-next'}) != None:
            return "http://flibusta.is" + soup.find('li', {'class': 'pager-next'}).find('a')['href']
        else:
            return ""

    def open_book_info(self, event):
        if self.List.curselection() != ():
            item = self.List.get(self.List.curselection())
            if item in self.text:
                index = self.text.index(item)
                href = self.anchor[index]
                app = None
                if str(href).find('/b/') != -1:
                    app = source.BookInfo.main("http://flibusta.is" + href, self.master)
                elif str(href).find('/sequence/') != -1:
                    app = source.Sequence.main(self.master, "http://flibusta.is" + href)
                elif str(href).find('/a/') != -1:
                    app = source.OpenAuthorInfo.main(self.master, "http://flibusta.is" + href)
                if app != None:
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