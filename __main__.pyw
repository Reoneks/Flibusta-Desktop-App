import tkinter as tk
import pyglet
import easygui
import source.FindBook
import source.LastBooks
import source.Genre
import source.OpenBook
import source.Library

class Example(tk.Frame):
 
    def __init__(self):
        super().__init__()
        self.init_UI()
 
    def init_UI(self):
        self.master.title("Flibusta Desktop App")
        for i in range(7):
            self.rowconfigure(i, pad=6)
        Hello = tk.Label(
            self,
            text="Добро пожаловать в Flibusta Desktop App!!!",
            fg="blue",
            font=("Konstanting", 30)
        )
        ContinueReading = tk.Button(
            self,
            text="Продолжить чтение",
            width=23,
            height=1,
            font=("Times New Roman",15),
            command=self.open_last_book
        )
        OpenBook = tk.Button(
            self,
            text="Открыть книгу",
            width=23,
            height=1,
            font=("Times New Roman",15),
            command=self.open_book
        )
        LastBooks = tk.Button(
            self,
            text="Последние поступления",
            width=23,
            height=1,
            font=("Times New Roman",15),
            command=self.last_books
        )
        Genre = tk.Button(
            self,
            text="Жанры",
            width=23,
            height=1,
            font=("Times New Roman",15),
            command=self.genres
        )
        FindBook = tk.Button(
            self,
            text="Поиск книги",
            width=23,
            height=1,
            font=("Times New Roman",15),
            command=self.find_book
        )
        Library = tk.Button(
            self,
            text="Библиотека",
            width=23,
            height=1,
            font=("Times New Roman",15),
            command=self.open_library
        )
        Hello.grid(column = 0, row = 0)
        ContinueReading.grid(column = 0, row = 1)
        OpenBook.grid(column = 0, row = 2)
        LastBooks.grid(column = 0, row = 3)
        Genre.grid(column = 0, row = 4)
        FindBook.grid(column = 0, row = 5)
        Library.grid(column = 0, row = 6)
        self.pack()
    
    def find_book(self):
        app = source.FindBook.main(self.master)
        app.bind("<<Close>>", self.on_close_app, '+')
        self.master.withdraw()
    
    def last_books(self):
        app = source.LastBooks.main(self.master)
        app.bind("<<Close>>", self.on_close_app, '+')
        self.master.withdraw()

    def genres(self):
        app = source.Genre.main(self.master)
        app.bind("<<Close>>", self.on_close_app, '+')
        self.master.withdraw()
    
    def open_book(self):
        file = easygui.fileopenbox(default = "C:\\*.fb2;*.fb2.zip", filetypes = [["*.fb2",".fb2.zip","Fb2"],"All Files","*"])
        if file != None:
            app = source.OpenBook.main(self.master,None,file)
            app.bind("<<Close>>", self.on_close_app, '+')
            self.master.withdraw()
    
    def open_last_book(self):
        app = source.OpenBook.main(self.master, LastBook = True)
        app.bind("<<Close>>", self.on_close_app, '+')
        self.master.withdraw()

    def open_library(self):
        app = source.Library.main(self.master)
        app.bind("<<Close>>", self.on_close_app, '+')
        self.master.withdraw()
    
    def on_close_app(self, event):
        self.master.deiconify()

def main():
    root = tk.Tk()
    app = Example()
    root.mainloop()

if __name__ == '__main__':
    pyglet.font.add_file('./fonts/20179.ttf')
    main()