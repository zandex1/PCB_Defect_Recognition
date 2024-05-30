from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import cv2
from PIL import Image, ImageTk
import util
import time

import ebb_motion as ebb_command
import ebb_serial_my as ebb_serial

from settings import Settings
from open_project import OpenProject
from create_project import CreateProject


class MainWindow:
    def __init__(self):
        self.main_window = Tk()
        width= self.main_window.winfo_screenwidth() 
        height= self.main_window.winfo_screenheight()
        #setting tkinter window size
        self.main_window.geometry("%dx%d" % (width, height)) 
        self.main_window.title('Гланое окно')
        
        self.alignment_enable = True
        self.recognition_enable = False
        ebb_command.main()
        self.x_now=0
        self.y_now=0
        
        self.state = False
        self.ser = ebb_serial.testPort('/dev/ttyACM0')
        
        self.menubar = Menu(self.main_window,background='white', foreground='black', activebackground='white', activeforeground='black')
        self.file = Menu(self.menubar,tearoff=0, background='white', foreground='black')
        self.file.add_command(label='Создать', command=self.create_project)
        self.file.add_command(label='Открыть', command=self.open_project)
        self.file.add_command(label='Настройки', command=self.open_settings)
        self.menubar.add_cascade(label='Файл', menu=self.file)
        self.main_window.config(menu=self.menubar)
        
        self.notebook = ttk.Notebook()
        self.notebook.grid(row=0,column=0)
        
        self.alignment = ttk.Frame(self.notebook)
        self.recognition = ttk.Frame(self.notebook)
                    
        self.webcam_label = Label(self.alignment)
        self.webcam_label.grid(row=0, column=0, rowspan=6, columnspan=6)
        
        self.b_to_ZERO =  Button(self.alignment, text='Вернуть на стартовую позицию', command=self.to_Zero)
        self.b_move_up =  Button(self.alignment, text='Вверх', command=self.move_up)
        self.b_move_down =  Button(self.alignment, text='Вниз', command=self.move_down)
        self.b_move_left =  Button(self.alignment, text='Влево', command=self.move_left)
        self.b_move_right =  Button(self.alignment, text='Вправо', command=self.move_right)
        self.b_scanning = Button(self.alignment, text='Сканирование', command = self.start_scaninng)
        
        self.l_x_cord = Label(self.alignment,text=f'X= {self.x_now} Y= {self.y_now}')
        self.e_value = Entry(self.alignment)
        
        self.b_to_ZERO.grid(row=0, column=7, columnspan=3)
        self.l_x_cord.grid(row=1,column=7)
        self.e_value.grid(row=2, column=7, columnspan=3)
        self.b_move_up.grid(row=3, column=8)
        self.b_move_left.grid(row=4, column=7)
        self.b_move_down.grid(row=4, column=8)
        self.b_move_right.grid(row=4, column=9)
        self.b_scanning.grid(row=5, column=7, columnspan=3)
        
        self.add_webcam(self.webcam_label)
        
        
        """
        РАСПОЗНАВАНИЕ
        """
        
        self.reference_image = ImageTk.PhotoImage(Image.open('003.jpg').resize((800,400)))
        self.inspected_image = ImageTk.PhotoImage(Image.open('003.jpg').resize((800,400)))
        self.PCB_image = ImageTk.PhotoImage(Image.open('PCB.jpg').resize((800,400)))
        
        self.reference_image_label = Label(self.recognition, image=self.reference_image)
        self.inspected_image_label = Label(self.recognition, image=self.inspected_image)
        self.PCB_image_label = Label(self.recognition, image=self.PCB_image)
        
        self.b_recognize = Button(self.recognition, text='Распознать', command='')
        self.b_next = Button(self.recognition, text='Следующий', command='')
        self.b_previous = Button(self.recognition, text='Предыдущий', command='')
        
        columns = ('ID','Correct','Component')
        
        self.table = ttk.Treeview(self.recognition,columns=columns,show="headings")
        
        self.table.heading("ID", text="ID", anchor=W)
        self.table.heading("Correct", text="Прваильно?", anchor=W)
        self.table.heading("Component", text="Компонент", anchor=W)
        
        self.table.column("#1", stretch=NO)
        self.table.column("#2", stretch=NO)
        self.table.column("#3", stretch=NO)
        
        SMDs = [(1, True, 'Резистор'),(2, False, 'Конденсатор'),(3, True, 'Конденсатор'),
                (4, False, 'Не установлен'),(5, True, 'Резистор'),(6, True, 'Резистор'),
                (7, True, 'Резистор'),(8, True, 'Резистор'),(9, True, 'Резистор')]
        
        for SMD in SMDs:
            self.table.insert("", END, values=SMD)     
        
        self.reference_image_label.grid(row=0,column=0, rowspan=3, columnspan=4)
        self.inspected_image_label.grid(row=0,column=5, rowspan=3, columnspan=4)
        self.PCB_image_label.grid(row=6,column=0, rowspan=3, columnspan=4)
        
        self.b_recognize.grid(row=6,column=4)
        self.b_next.grid(row=7,column=4)
        self.b_previous.grid(row=8,column=4)
        
        self.table.grid(row=6,column=5, rowspan=3, columnspan=4)
                
        # добавляем фреймы в качестве вкладок
        self.notebook.add(self.alignment, text="Юстировка")
        self.notebook.add(self.recognition, text='Распознавание')

    def start_scaninng(self):
        ebb_command.grid_prepare(self.ser,self.y_now, self.x_now, 25, 25, self.cap)
        self.to_Zero()

    def to_Zero(self):
        ebb_command.sendEnableMotors(self.ser, 1)
        ebb_command.state_ZERO_XY(self.ser)
        ebb_command.sendEnableMotors(self.ser, 0)
        self.x_now=0
        self.y_now=0
        self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        
    def move_right(self):
        if self.x_now + int(self.e_value.get()) <=100000:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, int(self.e_value.get()), 0, 500)
            ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.x_now += int(self.e_value.get())
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        elif self.x_now!=100000:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, (100000-self.x_now), 0, 500)
            
            ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.x_now = 100000
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        else:
            showerror(title='Ошибка', message='Конец по оси Х')
    
    def move_left(self):
        if self.x_now - int(self.e_value.get())>=0:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, int(self.e_value.get())*-1, 0, 500)
            
            ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.x_now -=int(self.e_value.get())
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        elif self.x_now != 0:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0-self.x_now, 0, 500)
            
            ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.x_now = 0
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        else:
            showerror(title='Ошибка', message='Конец по оси Х')
    
    def move_up(self):
        if self.y_now - int(self.e_value.get())>=0:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0, int(self.e_value.get())*-1, 500)
            
            ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)   
            self.y_now -=int(self.e_value.get())
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        elif self.y_now !=0:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0, 0-self.y_now, 500)
            time.sleep(2)
            
            ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.y_now = 0
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        else:
            showerror(title='Ошибка', message='Конец по оси Y')
    
    def move_down(self):
        if self.y_now + int(self.e_value.get())<=20000:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0, int(self.e_value.get()), 500)
            
            ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.y_now +=int(self.e_value.get())
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        elif self.y_now != 20000:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0, 20000-self.y_now, 500)
            
            ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.y_now = 20000
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        else: 
            showerror(title='Ошибка', message='Конец по оси Y')
                
    def add_webcam(self, label):

        self.cap = util.get_cap()
        
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        frame = cv2.line(frame, (415,80),(415,460),(0,0,255),3)
        frame = cv2.line(frame, (235,270),(595,270),(0,0,255),3)
        if self.notebook.select() == '.!notebook.!frame':
            self.most_recent_capture_arr = frame
            img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
            self.most_recent_capture_pil = Image.fromarray(img_)
            imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
            self._label.imgtk = imgtk
            self._label.configure(image=imgtk)
        #elif self.notebook.select() == '.!notebook.!frame1':
              

        self._label.after(20, self.process_webcam)

    def create_project(self):
        createproject = CreateProject()
        
    def open_project(self):
        openproject = OpenProject()
    
    def open_settings(self):
        settings = Settings()
    
    def start(self):
        self.main_window.mainloop()
        
if __name__ == "__main__":
    util.create_camera()
    app = MainWindow()
    app.start()