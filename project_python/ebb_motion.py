import time
import ebb_serial_my as ebb_serial_my
import cv2 as cv
import sys
import os

def doABMove(port_name, delta_a, delta_b, duration):
    # Issue command to move A/B axes as: "XM,<move_duration>,<axisA>,<axisB><CR>"
    # Then, <Axis1> moves by <AxisA> + <AxisB>, and <Axis2> as <AxisA> - <AxisB>
    
    if port_name is not None:
        str_output = 'XM,{0},{1},{2}\r'.format(duration, delta_a, delta_b)
        print(str_output)
        ebb_serial_my.command(port_name, str_output)

def doTimedPause(port_name, n_pause):
    if port_name is not None:
        while n_pause > 0:
            if n_pause > 750:
                td = 750
            else:
                td = n_pause
                if td < 1:
                    td = 1  # don't allow zero-time moves
            ebb_serial_my.command(port_name, 'SM,{0},0,0\r'.format(td))
            n_pause -= td

def doXYMove(port_name, delta_x, delta_y, duration):
    # duration is an integer in the range from 1 to 16777215, giving time in milliseconds
    # delta_x and delta_y are integers, each in the range from -16777215 to 16777215, giving movement distance in steps
    # The minimum speed at which the EBB can generate steps for each motor is 1.31 steps/second. The maximum
    # speed is 25,000 steps/second.
    # Move X/Y axes as: "SM,<move_duration>,<axis1>,<axis2><CR>"
    # Typically, this is wired up such that axis 1 is the Y axis and axis 2 is the X axis of motion.
    # On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
    if port_name is not None:
        str_output = 'SM,{0},{1},{2}\r'.format(duration,delta_y,delta_x)
        ebb_serial_my.command(port_name, str_output)

def sendEnableMotors(port_name, res):
    if res < 0:
        res = 0
    if res > 5:
        res = 5
    if port_name is not None:
        ebb_serial_my.command(port_name, 'EM,{0},{0}\r'.format(res))
        # If res == 0, -> Motor disabled
        # If res == 1, -> 16X microstepping
        # If res == 2, -> 8X microstepping
        # If res == 3, -> 4X microstepping
        # If res == 4, -> 2X microstepping
        # If res == 5, -> No microstepping

def limit_stop_y(ser): 
    global flag_limit_Y     
    a=ebb_serial_my.query(ser,"PI,C,6\r") # read pin PC6    
    try:       
        if  int(a[3]):
            flag_limit_Y=True                    
    except:    
        print ("ERROR Y")           
        return 0      
                
def limit_stop_x(ser): 
    global flag_limit_X
    b=ebb_serial_my.query(ser,"PI,A,2\r") # read pin PD4
    try:             
        if  int(b[3]):
            flag_limit_X=True  
    except:
        print ("ERROR X")
        return 0

def limit_stop_btn_config(ser):                
    ebb_serial_my.query(ser,"PD,C,6,1\r") # config pin PC6 as input
    ebb_serial_my.query(ser,"PD,A,2,1\r") # config pin PC7 as input
        
def state_ZERO_XY(ser):     
    global flag_limit_Y     
    global flag_limit_X
    #sendPenUp(ser, pen_up_delay_ms)
    
    while (flag_limit_Y==False) :
       limit_stop_y(ser)
       #print("flag_limit_Y=",flag_limit_Y) 
       doABMove(ser,-30,0,15)
    
    while (flag_limit_Y==True)  and (flag_limit_X==False) :
       limit_stop_x(ser)
       #print("flag_limit_X=",flag_limit_X) 
       doABMove(ser,0,-30,15)
    
    flag_limit_X=False
    flag_limit_Y=False 
    doTimedPause(ser,300)

def long_pause(ser,seconds):
    for i in range(seconds*2):
        doTimedPause(ser,500)        

def grid_prepare(ser, X_len, Y_len, X_grid, Y_grid, cap=None):

    number_of_image=1

    # cap = cv.VideoCapture('/dev/video3')
    # cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    # cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Костыль
    X_len+=500
    Y_len+=500
    X_grid+=1
    Y_grid+=1
    
    d_x=0
    d_y=0
  
    global arr_out   
    global flag_touch_push
  
    sendEnableMotors(ser,1)
 
    state_ZERO_XY(ser) 
    time.sleep(15)
    long_pause(ser,1)
    
    i=0
   
    d_x1=0
    d_y1=0
    d_y2=0
    d_x2=0
   
    X_stp = (X_len/(X_grid))  
    Y_stp = (Y_len/(Y_grid))
    arr=[[[0, 0]] * (X_grid) for i in range(Y_grid)]
   
    for y in range(Y_grid):     
        for x in range(X_grid):
            a= int((x*X_stp)+(X_stp/2))
            b =int((y*Y_stp)+(Y_stp/2))
            arr[x][y] = [a,b]
   
    for x in range(1,X_grid,2):  #переворот строки через строку (змейка)
        arr[x]=arr[x][::-1]

    arr_out=[[0,0]]*(X_grid*Y_grid)
    arr_out=sum(arr,[])
  
    start_x=0
    start_y=0
    delta_x=X_len/X_grid
    delta_y=Y_len/Y_grid
    k=1
    for x in range(0,X_grid):
       
        if x != 0:
            start_x=start_x+delta_x
        else:
            start_x=0

        for y in range(0,Y_grid):
           
            d_x1=arr[x][y][0]
            d_y1=arr[x][y][1]
           
            d_x=d_x1-d_x2
            d_y=d_y1-d_y2
          
            print(d_x,d_y)
            
            if not cap.isOpened():
                    sendEnableMotors(ser,0)
                    sys.exit("Cannot open camera")
            ret, frame = cap.read()
            if not ret:
                    sendEnableMotors(ser,0)
                    sys.exit("Cannot receive frame")
           
            writeStatus = cv.imwrite(f"{k}.jpg", img=frame)
            k+=1
            # writeStatus = cv.imwrite(str(start_x)+"_"+str(start_y)+ ".jpg", img=frame)
            if writeStatus is True:
                print("image written")
            else:
                sys.exit("Cannot save frame")

            doABMove(ser,d_y,d_x,500)
          
            #cv.imshow('frame', frame)
            doTimedPause(ser,1000)
            ##doTimedPause(ser,50)
        
            number_of_image = number_of_image + 1
            if x ==0 or x%2==0:
                start_y= start_y+delta_y
            else:
                start_y= start_y-delta_y
            d_x2=d_x1
            d_y2=d_y1
        if x == 0 or x%2==0:
            start_y=Y_len-delta_y
        if x!=0 and x%2!=0:
            start_y = 0
    
    sendEnableMotors(ser,0)
    print("Scaning finish succsefully")

def heatup_moves(ser):
    MAX_SPEED = 25000  # steps/s
       
    DY = 1620*6
    DX = 2120*6
    DT = 4000
    dist = max(DX, DY)
    speed = int(dist * 1000 / DT)
    assert speed < MAX_SPEED, 'Too fast!'
    time.sleep(1)

    sendEnableMotors(ser,   1)
    print("Отладка")
   
def main():
    global flag_touch_push
    global flag_limit_X
    global flag_limit_Y
    flag_touch_push=False
    flag_limit_X=False
    flag_limit_Y=False