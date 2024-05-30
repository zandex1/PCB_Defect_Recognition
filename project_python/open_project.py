from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
from tkinter import filedialog

import os

class OpenProject:
    def __init__(self) -> None:
        self.top = Toplevel()
        self.top.title('Открыть проект')
        
        l_path = Label(self.top, text='Путь к проекту')
                
        self.var_path = StringVar()
        self.entry_path = Entry(self.top, textvariable=self.var_path)
        
        self.btn_find = Button(self.top, text='...', command=self.browseFiles)
        self.btn_cancel = Button(self.top, text='Отмена', command=self.top.destroy)
        self.btn_open = Button(self.top, text='Открыть', command='')
        
        l_path.grid(row=2, column=0)
        self.entry_path.grid(row=3,column=0, columnspan=3)
        self.btn_find.grid(row=3,column=3)
        self.btn_cancel.grid(row=4,column=2)
        self.btn_open.grid(row=4,column=3)
        
    def browseFiles(self):
        filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a Project File",
                                          filetypes = (("JSON files",
                                                        "*.json*"),
                                                       ("all files",
                                                        "*.*")))
        self.entry_path.delete(0,'end')
        self.entry_path.insert(0, filename)
        
        self.top.destroy()