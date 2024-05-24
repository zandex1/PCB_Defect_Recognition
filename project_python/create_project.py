from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import cv2
from PIL import Image, ImageTk
import os
import util
import time

class CreateProject:
    def __init__(self) -> None:
        top = Toplevel()
        
        var = StringVar()
        entry = Entry(top, textvariable=var)
        #entry.pack(padx=60,pady=50)
        
        #self.frame.pack(padx=10,pady=10)