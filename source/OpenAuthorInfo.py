import tkinter as tk
from tkinter import Scrollbar
import requests
from io import BytesIO
from PIL import ImageTk, Image
from bs4 import BeautifulSoup
import os.path
import webbrowser
import source.BookInfo

class Example(tk.Toplevel):
 
    def __init__(self, master = None):
        super().__init__(master = master)
        self.init_UI()
 
    def init_UI(self):
        self.title("Автор")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.img = ImageTk.PhotoImage(Image.open(os.getcwd()+"/images/No_image.png"))
        self.panel = tk.Label(
            self,
            image=self.img,
            background="white",
            height=400,
            width=300
        )
        self.Author = tk.Label(
            self,
            text="Произошла ошибка при попытке получить информацию о авторе.",
            font=("Times New Roman",15)
        )
        self.Annotation = tk.Text(
            self,
            font=("Times New Roman",12),
            height=17,
            width=70,
            wrap=tk.WORD
        )
        self.List = tk.Listbox(
            self,
            height=4,
            font=("TkDefaultFont", 12)
        )
        Scroll = Scrollbar(self, orient=tk.VERTICAL)
        self.Books = tk.Listbox(
            self,
            yscrollcommand = Scroll.set,
            height=20,
            font=("TkDefaultFont", 12)
        )
        self.List.bind("<<ListboxSelect>>", self.open_autor_webpage)
        self.Books.bind("<<ListboxSelect>>", self.open_book)
        Scroll.config(command = self.Books.yview)
        self.Author.grid(sticky=tk.N, column = 0, row = 0, columnspan=3, padx = 5)
        self.panel.grid(column = 0, row = 1, rowspan=2, padx = 2, pady = 3)
        self.Annotation.grid(sticky=tk.W+tk.E, column = 1, row = 1, padx = 5, pady = 3)
        self.List.grid(sticky=tk.W+tk.E, column = 1, row = 2, padx = 3)
        self.Books.grid(sticky=tk.W+tk.E, column = 0, row = 3, pady = 3, columnspan = 2)
        Scroll.grid(sticky=tk.E+tk.N+tk.S, column = 2, row = 3, pady = 3)
    
    def open_autor_webpage(self, event):
        if self.List.curselection() != ():
            item = self.List.get(self.List.curselection())
            index = self.text1.index(item)
            webbrowser.open_new_tab(self.anchor1[index])

    def open_book(self, event):
        if self.Books.curselection() != ():
            item = self.Books.get(self.Books.curselection())
            index = self.text.index(item)
            app = source.BookInfo.main("http://flibusta.is" + self.anchor[index], self.master)
            app.bind("<<Close>>", self.on_close_app, '+')
            self.withdraw()

    def parse(self, url):
        self.text = []
        self.anchor = []
        self.text1 = []
        self.anchor1 = []
        htmldata = requests.get(url)
        soup = BeautifulSoup(htmldata.content,'lxml')
        self.Author['text'] = soup.find('div', {'class': 'clear-block', 'id': 'main'}).find('h1', {'class': 'title'}).text
        image_data = soup.find('div', {'id': 'divabio'}).find('img')
        if image_data != None:
            img_url = "http://flibusta.is" + image_data['src']
            if ImageTk.PhotoImage(Image.open(BytesIO(requests.get(img_url).content))).__sizeof__() > 0:
                self.img = ImageTk.PhotoImage(Image.open(BytesIO(requests.get(img_url).content)).resize((300,400)))
                self.panel.config(image = self.img)
        self.Annotation.insert(tk.END, soup.find('div', {'id': 'divabio'}).find('p').text)
        self.text1 = soup.find('div', {'id': 'divabio'}).find('a').parent.text.split("\n")
        for i in self.text1:
            self.List.insert(tk.END, i)
        for i in soup.find('div', {'id': 'divabio'}).find_all('a'):
            self.anchor1.append(i['href'])
        for i in soup.find('form', {'method': 'POST'}).find_all('a'):
            if str(i['href']).find('/b/') != -1 and len(str(i['href']).split("/")) == 3:
                self.text.append(i.text.replace("\n",""))
                self.Books.insert(tk.END,self.text[len(self.text)-1])
                self.anchor.append(i['href'])
    
    def on_closing(self):
        self.event_generate("<<Close>>")
        self.destroy()
        
    def on_close_app(self, event):
        self.deiconify()

def main(master, url):
    app = Example(master)
    app.parse(url)
    return app