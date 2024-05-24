from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror,showinfo
import cv2
from PIL import Image, ImageTk
import os
import util
import time

import ebb_motion as ebb_command
import ebb_serial_my as ebb_serial

class Settings:
    def __init__(self) -> None:
        settings_window = Toplevel()
        settings_window.geometry("410x390+350+100")
        settings_window.title('Настройки')
        
        self.notebook_settings = ttk.Notebook(settings_window)
        self.notebook_settings.grid(row=0, column=0, columnspan=2)
        
        # Усилитель видеопроцессора
        self.settings_videoprocessor = ttk.Frame(self.notebook_settings)
        self.settings_stand = ttk.Frame(self.notebook_settings)
        
        self.l_brightnes = Label(self.settings_videoprocessor, text='Яркость')
        self.s_brightnes = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_brightnes = Entry(self.settings_videoprocessor)
        
        self.l_brightnes.grid(row=0, column=0)
        self.s_brightnes.grid(row=0, column=1) 
        self.e_brightnes.grid(row=0, column=2)
        
        self.l_contrast = Label(self.settings_videoprocessor, text='Контрастность')
        self.s_contrast = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_contrast = Entry(self.settings_videoprocessor)
        
        self.l_contrast.grid(row=1, column=0)
        self.s_contrast.grid(row=1, column=1) 
        self.e_contrast.grid(row=1, column=2)
        
        self.l_saturation = Label(self.settings_videoprocessor, text='Насыщенность')
        self.s_saturation = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_saturation = Entry(self.settings_videoprocessor)
        
        self.l_saturation.grid(row=3, column=0)
        self.s_saturation.grid(row=3, column=1) 
        self.e_saturation.grid(row=3, column=2)
        
        self.l_clarity = Label(self.settings_videoprocessor, text='Четкость')
        self.s_clarity = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_clarity = Entry(self.settings_videoprocessor)
        
        self.l_clarity.grid(row=4, column=0)
        self.s_clarity.grid(row=4, column=1) 
        self.e_clarity.grid(row=4, column=2)
        
        self.l_gamma = Label(self.settings_videoprocessor, text='Гамма')
        self.s_gamma = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_gamma = Entry(self.settings_videoprocessor)
        
        self.l_gamma.grid(row=5, column=0)
        self.s_gamma.grid(row=5, column=1) 
        self.e_gamma.grid(row=5, column=2)
        
        self.l_white_balance = Label(self.settings_videoprocessor, text='Баланс белого')
        self.s_white_balance = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_white_balance = Entry(self.settings_videoprocessor)
        
        self.l_white_balance.grid(row=6, column=0)
        self.s_white_balance.grid(row=6, column=1) 
        self.e_white_balance.grid(row=6, column=2)
        
        self.l_gain = Label(self.settings_videoprocessor, text='Усиление')
        self.s_gain = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_gain = Entry(self.settings_videoprocessor)
        
        self.l_gain.grid(row=7, column=0)
        self.s_gain.grid(row=7, column=1) 
        self.e_gain.grid(row=7, column=2)
        
        self.b_return_to_common = Button(self.settings_videoprocessor, text='По умолчанию')
        
        self.b_return_to_common.grid(row=8, column=1)
        
        # Управление стендом
        self.l_selected_camera = Label(self.settings_stand, text='Камера')
        self.cb_selected_camera = ttk.Combobox(self.settings_stand,values=['/dev/video0','/dev/video1'])
        
        self.l_selected_camera.grid(row=0, column=0)
        self.cb_selected_camera.grid(row=0, column=2)
        
        self.l_selected_COM = Label(self.settings_stand, text='COM порт')
        self.cb_selected_COM = ttk.Combobox(self.settings_stand,values=['/dev/video0','/dev/video1'])
        
        self.l_selected_COM.grid(row=1, column=0)
        self.cb_selected_COM.grid(row=1, column=2)
        
        self.l_scale = Label(self.settings_stand, text='Масштаб')
        self.s_scale = Scale(self.settings_stand, from_=0, to=100, orient='horizontal')
        self.e_scale = Entry(self.settings_stand)
        
        self.l_scale.grid(row=2, column=0)
        self.s_scale.grid(row=2, column=1) 
        self.e_scale.grid(row=2, column=2)
        
        self.l_focus = Label(self.settings_stand, text='Фокус')
        self.s_focus = Scale(self.settings_stand, from_=0, to=100, orient='horizontal')
        self.e_focus = Entry(self.settings_stand)
        
        self.l_focus.grid(row=3, column=0)
        self.s_focus.grid(row=3, column=1) 
        self.e_focus.grid(row=3, column=2)
        
        self.l_shutter = Label(self.settings_stand, text='Выдержка')
        self.s_shutter = Scale(self.settings_stand, from_=0, to=100, orient='horizontal')
        self.e_shutter = Entry(self.settings_stand)
        
        self.l_shutter.grid(row=4, column=0)
        self.s_shutter.grid(row=4, column=1) 
        self.e_shutter.grid(row=4, column=2)
        
        self.l_speed_aperture = Label(self.settings_stand, text='Диафрагма')
        self.s_speed_aperture = Scale(self.settings_stand, from_=0, to=100, orient='horizontal')
        self.e_speed_aperture = Entry(self.settings_stand)
        
        self.l_speed_aperture.grid(row=5, column=0)
        self.s_speed_aperture.grid(row=5, column=1) 
        self.e_speed_aperture.grid(row=5, column=2)
        
        # добавляем фреймы в качестве вкладок
        self.notebook_settings.add(self.settings_videoprocessor, text="Усилитель видеопроцессора")
        self.notebook_settings.add(self.settings_stand, text="Управление стендом")
        
        self.btn_OK = Button(settings_window, text='Ок')
        self.btn_accept = Button(settings_window, text='Применить')
        
        self.btn_OK.grid(row=1,column=0)
        self.btn_accept.grid(row=1,column=1)
        

    def start(self):
        self.frame.mainloop()   
