import tkinter as tk
from tkinter import Scrollbar
import requests
from zipfile import ZipFile
import os.path
import io
from io import BytesIO
import codecs
import base64
from PIL import ImageTk, Image
from pathlib import Path
from bs4 import BeautifulSoup
import sqlite3

class Example(tk.Toplevel):
 
    def __init__(self, master = None):
        super().__init__(master = master)
        self.init_UI()
 
    def init_UI(self):
        self.title("Книга")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.book_url = ""
        self.path = ""
        self.Scroll = Scrollbar(self, orient=tk.VERTICAL)
        self.Book_Text = tk.Text(
            self,
            yscrollcommand = self.Scroll.set,
            width = 196,
            height = 33,
            wrap = tk.WORD,
            spacing3 = 10,
            spacing2 = 2,
            state = tk.DISABLED,
            borderwidth=5,
            relief=tk.FLAT
        )
        self.Scroll.config(command = self.Book_Text.yview)
        self.Book_Text.grid(row = 0, column = 0, sticky = tk.N+tk.W+tk.E+tk.S)
        self.Scroll.grid(row = 0, column = 1, sticky = tk.N+tk.S)
    
    def parse(self, url):
        self.book_url = url
        self.images=[]
        url += "/read"
        htmldata = requests.get(url)
        soup = BeautifulSoup(htmldata.content,'lxml')
        self.Book_Text.configure(state = tk.NORMAL)
        self.Book_Text.tag_configure("Center", justify='center', font=('Verdana', 15, 'bold'))
        self.Book_Text.tag_configure("Subtitle", font=("TkDefaultFont", 12, 'bold'))
        self.Book_Text.tag_configure("Strong", font=("TkDefaultFont", 10, 'bold'))
        self.Book_Text.tag_configure("P", font=("TkDefaultFont", 10))
        self.Book_Text.tag_configure("Emphasis", font=("TkDefaultFont", 10, 'italic'))
        self.Book_Text.tag_configure("StrongEmphasis", font=("TkDefaultFont", 10, 'bold italic'))
        for i in soup.find('div', {'class': 'clear-block', 'id': 'main'}).find_all(['p','h3','img']):
            if i.name == 'p' and i.has_attr('class') and i['class'][0] == 'book':
                text = ' '.join(i.text.replace("\n"," ").split())
                self.Book_Text.insert(tk.END, "    ", 'P')
                for k in i.find_all(['i','b']):
                    if k.name == "strong" and k.find('i') != None:
                        self.Book_Text.insert(tk.END, text.split(' '.join(k.text.split()), 1)[0], 'P')
                        text = text.split(' '.join(k.text.split()), 1)[1]
                        temp_text = ' '.join(k.text.split())
                        for u in k.find_all('i'):
                            self.Book_Text.insert(tk.END, temp_text.split(' '.join(u.text.split()), 1)[0], 'Strong')
                            self.Book_Text.insert(tk.END, ' '.join(u.text.split()), 'StrongEmphasis')
                            temp_text = temp_text.split(' '.join(u.text.split()), 1)[1]
                        self.Book_Text.insert(tk.END, temp_text, 'Strong')
                    elif k.name == "i" and k.find('b') != None:
                        self.Book_Text.insert(tk.END, text.split(' '.join(k.text.split()), 1)[0], 'P')
                        text = text.split(' '.join(k.text.split()), 1)[1]
                        temp_text = ' '.join(k.text.split())
                        for u in k.find_all('b'):
                            self.Book_Text.insert(tk.END, temp_text.split(' '.join(u.text.split()), 1)[0], 'Emphasis')
                            self.Book_Text.insert(tk.END, ' '.join(u.text.split()), 'StrongEmphasis')
                            temp_text = temp_text.split(' '.join(u.text.split()), 1)[1]
                        self.Book_Text.insert(tk.END, temp_text, 'Emphasis')
                    else:
                        if k.parent.name == "p":
                            self.Book_Text.insert(tk.END, text.split(' '.join(k.text.split()), 1)[0], 'P')
                            style = ""
                            if k.name == "b":
                                style = "Strong"
                            else:
                                style = "Emphasis"
                            self.Book_Text.insert(tk.END, ' '.join(k.text.split()), style)
                            text = text.split(' '.join(k.text.split()), 1)[1]
                self.Book_Text.insert(tk.END, text + "\n", 'P')
            elif i.name == 'img':
                img_url = "http://flibusta.is" + i['src']
                if ImageTk.PhotoImage(Image.open(BytesIO(requests.get(img_url).content))).__sizeof__() > 0:
                    image = ImageTk.PhotoImage(Image.open(BytesIO(requests.get(img_url).content)))
                    self.images.append(image)
                    self.Book_Text.image_create(tk.END, image = self.images[len(self.images)-1], align = "center", padx = self.winfo_screenwidth()/3 - 100)
                    self.Book_Text.insert(tk.END, "\n")
            elif i.name == 'h3' and i.has_attr('class') and i['class'][0] == 'book':
                    self.Book_Text.insert(tk.END, i.text + "\n", 'Center')
        self.Book_Text.configure(state = tk.DISABLED)
        conn = sqlite3.connect('./database/books.sqlite')
        c = conn.cursor()
        c.execute("SELECT ValueA, ValueB FROM [All books positions] WHERE url = ?", (self.book_url,))
        result = c.fetchone()
        if result != None:
            self.Book_Text.yview_moveto(result[0])
            self.Book_Text.xview_moveto(result[1])
        conn.close()

    def check_zip(self, path):
        self.path = path
        if os.path.splitext(path)[1] == ".zip":
            with ZipFile(path, 'r') as zipObj:
                listOfiles = zipObj.namelist()
                for elem in listOfiles:
                    if elem.split(".")[len(elem.split("."))-1] == "fb2":
                        self.parse_fb2(zipObj.read(elem).decode('utf-8'))
                        break
        else:
            fileObj = codecs.open(path, "r", "utf_8_sig")
            text = fileObj.read()
            fileObj.close()
            self.parse_fb2(text)
        conn = sqlite3.connect('./database/books.sqlite')
        c = conn.cursor()
        c.execute("SELECT ValueA, ValueB FROM [All books positions] WHERE path = ?", (self.path,))
        result = c.fetchone()
        if result != None:
            self.Book_Text.yview_moveto(result[0])
            self.Book_Text.xview_moveto(result[1])
        conn.close()
    
    def parse_fb2(self, text):
        self.images=[]
        soup = BeautifulSoup(text,'lxml')
        self.Book_Text.configure(state = tk.NORMAL)
        self.Book_Text.tag_configure("Center", justify='center', font=('Verdana', 15, 'bold'))
        self.Book_Text.tag_configure("Subtitle", font=("TkDefaultFont", 12, 'bold'))
        self.Book_Text.tag_configure("Strong", font=("TkDefaultFont", 10, 'bold'))
        self.Book_Text.tag_configure("P", font=("TkDefaultFont", 10))
        self.Book_Text.tag_configure("Emphasis", font=("TkDefaultFont", 10, 'italic'))
        self.Book_Text.tag_configure("StrongEmphasis", font=("TkDefaultFont", 10, 'bold italic'))
        self.Book_Text.insert(tk.END, soup.find('book-title').text + "\n", 'Center')
        for i in soup.find('body').find_all('section'):
            for j in i.select('section > p,title,subtitle,image,empty-line'):
                if j.name == 'title':
                    self.Book_Text.insert(tk.END, j.text + "\n", 'Center')
                elif j.name == 'subtitle':
                    self.Book_Text.insert(tk.END, "    " + j.text + "\n", 'Subtitle')
                elif j.name == 'empty-line':
                    self.Book_Text.insert(tk.END, "\n")
                elif j.name == 'image':
                    img_data = soup.find('binary', {'id': j['l:href'].replace("#","")}).text
                    base64_img_bytes = img_data.encode('utf-8')
                    decoded_image_data = base64.decodebytes(base64_img_bytes)
                    image = ImageTk.PhotoImage(data = decoded_image_data)
                    self.images.append(image)
                    self.Book_Text.image_create(tk.END, image = self.images[len(self.images)-1], align = "center", padx = self.winfo_screenwidth()/3 - 100)
                    self.Book_Text.insert(tk.END, "\n")
                else:
                    text = ' '.join(j.text.replace("\n"," ").split())
                    self.Book_Text.insert(tk.END, "    ", 'P')
                    for k in j.select('p > emphasis,strong'):
                        if k.name == "strong" and k.find('emphasis') != None:
                            self.Book_Text.insert(tk.END, text.split(' '.join(k.text.split()), 1)[0], 'P')
                            text = text.split(' '.join(k.text.split()), 1)[1]
                            temp_text = ' '.join(k.text.split())
                            for u in k.find_all('emphasis'):
                                self.Book_Text.insert(tk.END, temp_text.split(' '.join(u.text.split()), 1)[0], 'Strong')
                                self.Book_Text.insert(tk.END, ' '.join(u.text.split()), 'StrongEmphasis')
                                temp_text = temp_text.split(' '.join(u.text.split()), 1)[1]
                            self.Book_Text.insert(tk.END, temp_text, 'Strong')
                        elif k.name == "emphasis" and k.find('strong') != None:
                            self.Book_Text.insert(tk.END, text.split(' '.join(k.text.split()), 1)[0], 'P')
                            text = text.split(' '.join(k.text.split()), 1)[1]
                            temp_text = ' '.join(k.text.split())
                            for u in k.find_all('strong'):
                                self.Book_Text.insert(tk.END, temp_text.split(' '.join(u.text.split()), 1)[0], 'Emphasis')
                                self.Book_Text.insert(tk.END, ' '.join(u.text.split()), 'StrongEmphasis')
                                temp_text = temp_text.split(' '.join(u.text.split()), 1)[1]
                            self.Book_Text.insert(tk.END, temp_text, 'Emphasis')
                        else:
                            if k.parent.name == "p":
                                self.Book_Text.insert(tk.END, text.split(' '.join(k.text.split()), 1)[0], 'P')
                                style = ""
                                if k.name == "strong":
                                    style = "Strong"
                                else:
                                    style = "Emphasis"
                                self.Book_Text.insert(tk.END, ' '.join(k.text.split()), style)
                                text = text.split(' '.join(k.text.split()), 1)[1]
                    self.Book_Text.insert(tk.END, text + "\n", 'P')
        self.Book_Text.configure(state = tk.DISABLED)

    def on_closing(self):
        if self.book_url != "" or self.path != "":
            conn = sqlite3.connect('./database/books.sqlite')
            c = conn.cursor()
            data = (self.book_url, self.path)
            c.execute("UPDATE [Last book] SET url = ?, path = ?", data)
            c.execute("SELECT rowid FROM [All books positions] WHERE url = ? AND path = ?", data)
            result = c.fetchone()
            if result != None:
                data += (self.Book_Text.yview()[0], self.Book_Text.yview()[1], result[0])
                c.execute("UPDATE [All books positions] SET url = ?, path = ?, ValueA = ?, ValueB = ? WHERE rowid = ?", data)
            else:
                data += (self.Book_Text.yview()[0], self.Book_Text.yview()[1])
                c.execute("INSERT INTO [All books positions] VALUES(?,?,?,?)", data)
            conn.commit()
            conn.close()
        self.event_generate("<<Close>>")
        self.destroy()
    
    def open_last_book(self):
        conn = sqlite3.connect('./database/books.sqlite')
        c = conn.cursor()
        c.execute("SELECT * FROM [Last book] WHERE rowid = 1")
        data = c.fetchone()
        conn.close()
        if data[0] != "":
            self.parse(data[0])
        elif data[1] != "":
            self.check_zip(data[1])

def main(master, url = None, path = None, LastBook = False):
    app = Example(master)
    if url != None and url != "":
        app.parse(url)
    elif path != None and path != "":
        app.check_zip(path)
    elif LastBook:
        app.open_last_book()
    return app