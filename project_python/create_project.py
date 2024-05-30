from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
from tkinter import filedialog

import os

class CreateProject:
    def __init__(self) -> None:
        self.top = Toplevel()
        self.top.title('Создать проект')
        
        l_name = Label(self.top, text='Название проекта')
        l_path = Label(self.top, text='Путь к проекту')
        
        self.entry_name = Entry(self.top)
        
        self.entry_path = Entry(self.top)
        
        self.btn_find = Button(self.top, text='...', command=self.browseFiles)
        self.btn_cancel = Button(self.top, text='Отмена', command=self.top.destroy)
        self.btn_create = Button(self.top, text='Создать', command=self.createProject)
        
        l_name.grid(row=0, column=0)
        self.entry_name.grid(row=1,column=0, columnspan=3)
        l_path.grid(row=2, column=0)
        self.entry_path.grid(row=3,column=0, columnspan=3)
        self.btn_find.grid(row=3,column=3)
        self.btn_cancel.grid(row=4,column=2)
        self.btn_create.grid(row=4,column=3)
        
    def browseFiles(self):
        filename = filedialog.askdirectory(initialdir = "/",
                                          title = "Select a Folder")
        self.entry_path.delete(0,'end')
        self.entry_path.insert(0, filename)
    
    def createProject(self):
        
        os.mkdir(self.entry_path.get() + '/' + self.entry_name.get())
        os.mkdir(self.entry_path.get() + '/' + self.entry_name.get()+ '/reference')
        os.mkdir(self.entry_path.get() + '/' + self.entry_name.get()+ '/inspect')
        
        showinfo(title='Проект создан', message='Проект успешно создан')
        
        self.top.destroy()