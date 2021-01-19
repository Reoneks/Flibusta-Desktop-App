import tkinter as tk
import requests
from io import BytesIO
from PIL import ImageTk, Image
from bs4 import BeautifulSoup
import os.path
from tkinter.ttk import Combobox
import source.DownloadFile
import source.OpenBook
import re
import sqlite3

class Example(tk.Toplevel):
 
    def __init__(self, master = None):
        super().__init__(master = master)
        self.init_UI()
 
    def init_UI(self):
        self.title("Информация о книге")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.img = ImageTk.PhotoImage(Image.open(os.getcwd()+"/images/No_image.png"))
        self.Book = tk.Label(
            self,
            text="Произошла ошибка при попытке получить информацию о книге.",
            font=("Times New Roman",20)
        )
        self.Author = tk.Label(
            self,
            font=("Times New Roman",15)
        )
        self.Genre = tk.Label(
            self,
            font=("Times New Roman",12)
        )
        self.Series = tk.Label(
            self,
            font=("Times New Roman",12)
        )
        self.Grade = tk.Label(
            self,
            font=("Times New Roman",12)
        )
        self.Read = tk.Label(
            self,
            font=("Times New Roman",12),
            text="Читать",
            fg="blue",
            cursor="hand2"
        )
        self.Text = tk.Label(
            self,
            font=("Times New Roman",16),
            text="Аннотация:"
        )
        self.Annotation = tk.Text(
            self,
            font=("Times New Roman",12),
            height=13,
            width=100,
            wrap=tk.WORD
        )
        self.Download = Combobox(
            self, 
            state='readonly'
        )
        self.Library = Combobox(
            self, 
            state='readonly'
        )
        self.panel = tk.Label(
            self,
            image=self.img,
            background="white",
            height=300,
            width=200
        )
        self.Download.set('Скачать в формате')
        self.Download.bind("<<ComboboxSelected>>", self.download_book)
        self.Library.set('Добавить в библиотеку')
        self.Library.bind("<<ComboboxSelected>>", self.add_in_library)
        self.Read.bind("<Button-1>", self.read_book)
        self.panel.grid(column = 0, row = 0, rowspan=5, padx = 2)
        self.Book.grid(column = 1, row = 0, columnspan=4, padx = 5)
        self.Author.grid(column = 1, row = 1, columnspan=4, padx = 5)
        self.Genre.grid(column = 1, row = 2, columnspan=4, padx = 5)
        self.Series.grid(column = 1, row = 3, padx = 5)
        self.Read.grid(column = 2, row = 3, padx = 5)
        self.Download.grid(column = 3, row = 3, padx = 5)
        self.Library.grid(column = 4, row = 3, padx = 5)
        self.Grade.grid(column = 1, row = 4, columnspan=4)
        self.Text.grid(sticky=tk.W, column = 0, row = 5, padx = 5, pady = 7)
        self.Annotation.grid(sticky=tk.E+tk.W+tk.S, column = 0, row = 6, columnspan=5, padx = 3, pady = 3)

    def parse(self, url):
        self.book_url = url
        loaded = True
        try:
            htmldata = requests.get(url)
        except Exception as e:
            #!Error=str(e)
            loaded = False 
        if loaded:
            soup = BeautifulSoup(htmldata.content,'lxml')
            image_data = soup.find('img',{'alt': 'Cover image'})
            if image_data != None:
                img_url = "http://flibusta.is" + image_data['src']
            try:
                if ImageTk.PhotoImage(Image.open(BytesIO(requests.get(img_url).content))).__sizeof__() > 0:
                    self.img_data = requests.get(img_url).content
                    self.img = ImageTk.PhotoImage(Image.open(BytesIO(self.img_data)).resize((200,300)))
                    self.panel.config(image = self.img)
            except Exception as e:
                #!Error=str(e)
                loaded = False
            self.Book['text'] = ' '.join(re.sub(r'\([^()]*\)', '', soup.find('h1',{'class': 'title'}).text).split())
            self.Author['text'] = "Автор: Автор не указан"
            for i in soup.find('div', {'class': 'clear-block', 'id': 'main'}).select('div > a'):
                if str(i['href']).find('/a/') != -1:
                    self.Author['text'] = "Автор: " + i.text
                    break
            self.Genre['text'] = "Жанры: " + soup.find('p',{'class': 'genre'}).text
            if re.sub(r'\([^()]*\)', '', soup.find('p',{'class': 'genre'}).parent.select_one('div > a').text) != "":
                self.Series['text'] = "Серия книг: " + soup.find('p',{'class': 'genre'}).parent.select_one('div > a').text
            else:
                self.Series['text'] = "Серия книг: Не входит в серию книг"
            self.Grade['text'] = soup.find('div',{'id': 'newann'}).find('p').text
            if soup.select_one('div.clear-block > p') != None:
                self.Annotation.insert(tk.END, str(soup.select_one('div.clear-block > p').text))
                self.Annotation.configure(state="disabled")
            download_variants_bool = False
            download_variants = []
            for i in soup.find('p',{'class': 'genre'}).parent.select('div > a'):
                if i.text == "(читать)":
                    download_variants_bool = True
                    continue
                if download_variants_bool or (re.sub(r'\([^()]*\)', '', i.text) == "" and i.text != "(читать)"):
                    download_variants.append(i.text.replace("(","").replace(")","").replace("скачать ",""))
            self.Download['values'] = download_variants
            conn = sqlite3.connect('./database/books.sqlite')
            c = conn.cursor()
            c.execute("SELECT [Type name] FROM [Library types]")
            data = c.fetchall()
            self.Library['values'] = [i[0] for i in data]
            c.execute("SELECT Type FROM [Library] WHERE url = ?", (self.book_url,))
            result = c.fetchone()
            if result is not None:
                self.Library.current(int(result[0])-1)
            conn.close()
    
    def read_book(self, event):
        app = source.OpenBook.main(url = self.book_url, master = self.master)
        app.bind("<<Close>>", self.on_close_app, '+')
        self.withdraw()
    
    def download_book(self, event):
        source.DownloadFile.DownloadStart(self.book_url, self.Book['text'], event.widget.get())
    
    def on_closing(self):
        self.event_generate("<<Close>>")
        self.destroy()
        
    def on_close_app(self, event):
        self.deiconify()

    def add_in_library(self, event):
        conn = sqlite3.connect('./database/books.sqlite')
        c = conn.cursor()
        c.execute("SELECT rowid FROM [Library] WHERE url = ?", (self.book_url,))
        result = c.fetchone()
        if result != None:
            c.execute("SELECT rowid FROM [Library types] WHERE [Type name] = ?", (event.widget.get(),))
            data = (c.fetchone()[0], result[0])
            c.execute("UPDATE [Library] SET Type = ? WHERE rowid = ?", data)
        else:
            c.execute("SELECT rowid FROM [Library types] WHERE [Type name] = ?", (event.widget.get(),))
            data = (self.img_data, self.book_url, self.Book['text'], self.Author['text'], self.Genre['text'], self.Series['text'], self.Grade['text'], str(self.Annotation.get("1.0", tk.END)), ", ".join(self.Download['values']), c.fetchone()[0])
            c.execute("INSERT INTO [Library] VALUES(?,?,?,?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()

def main(url, master):
    try:
        if app.state() == "normal": app.focus()
    except NameError as e:
        app = Example(master)
        app.parse(url)
    return app