import tkinter as tk
from tkinter import Scrollbar
import requests
from bs4 import BeautifulSoup
import source.BookInfo
import source.OpenAuthorInfo

class Example(tk.Toplevel):
 
    def __init__(self, master = None):
        super().__init__(master = master)
        self.init_UI()
 
    def init_UI(self):
        self.title("Серия")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        Text = tk.Label(
            self,
            text="Автор: ",
            font=("Times New Roman",12)
        )
        Text1 = tk.Label(
            self,
            text="Жанры: ",
            font=("Times New Roman",12)
        )
        self.Author = tk.Label(
            self,
            text="не указан",
            font=("Times New Roman",12),
            fg="blue",
            cursor="hand2"
        )
        self.Genre = tk.Label(
            self,
            text="не указаны",
            font=("Times New Roman",12)
        )
        Scroll = Scrollbar(self, orient=tk.VERTICAL)
        self.List = tk.Listbox(
            self,
            yscrollcommand = Scroll.set,
            height=20,
            width=100,
            font=("TkDefaultFont", 12)
        )
        self.List.bind("<<ListboxSelect>>", self.open_book_info)
        self.Author.bind("<Button-1>", self.open_author_info)
        Scroll.config(command = self.List.yview)
        Text.grid(sticky=tk.W, column = 0, row = 0)
        Text1.grid(sticky=tk.W, column = 0, row = 1)
        self.Author.grid(sticky=tk.W, column = 1, row = 0)
        self.Genre.grid(sticky=tk.W, column = 1, row = 1)
        Scroll.grid(sticky=tk.E+tk.N+tk.S, column = 2, row = 2, padx = 3, pady = 5)
        self.List.grid(sticky=tk.W+tk.E, column = 0, row = 2, columnspan = 2, padx = 3, pady = 5)
    
    def parse(self, url):
        self.text = []
        self.anchor = []
        authors_and_genres = []
        self.author_link = ""
        htmldata = requests.get(url)
        soup = BeautifulSoup(htmldata.content,'lxml')
        for i in soup.find('div', {'class': 'clear-block', 'id': 'main'}).select_one('div.clear-block > table').find('tbody').find_all('tr'):
            for j in i.find_all('td'):
                text = ""
                for k in j.find_all('a'):
                    if self.author_link == "":
                        self.author_link = k['href']
                    text += k.text + " "
                if text != "":
                    authors_and_genres.append(text)
        if len(authors_and_genres) > 0:
            authors_and_genres[0] = ' '.join(authors_and_genres[0].split())
            self.Author['text'] = authors_and_genres[0]
            if len(authors_and_genres) > 1:
                authors_and_genres[1] = ', '.join(authors_and_genres[1].split())
                self.Genre['text'] = authors_and_genres[1]
        for i in soup.find('div', {'class': 'clear-block', 'id': 'main'}).select('div.clear-block > a'):
            if len(str(i['href']).split("/")) == 3 and str(i['href']).find('/b/') != -1:
                self.text.append("    " + i.text.replace("\n",""))
                self.List.insert(tk.END,self.text[len(self.text)-1])
                self.anchor.append(i['href'])
    
    def open_book_info(self, event):
        if self.List.curselection() != ():
            item = self.List.get(self.List.curselection())
            index = self.text.index(item)
            app = source.BookInfo.main("http://flibusta.is" + self.anchor[index], self.master)
            app.bind("<<Close>>", self.on_close_app, '+')
            self.withdraw()
    
    def open_author_info(self, event):
        app = source.OpenAuthorInfo.main(self.master, "http://flibusta.is" + self.author_link)
        app.bind("<<Close>>", self.on_close_app, '+')
        self.withdraw()
    
    def on_closing(self):
        self.event_generate("<<Close>>")
        self.destroy()
        
    def on_close_app(self, event):
        self.deiconify()

def main(master, url):
    app = Example(master)
    app.parse(url)
    return app