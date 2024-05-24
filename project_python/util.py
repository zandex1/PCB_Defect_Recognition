import cv2

def create_camera():
    global cap
    cap = cv2.VideoCapture(2, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    cap.set(cv2.CAP_PROP_FPS, 30)

def realese_camera():
    global cap
    cap.release()
    
def get_cap():
    global cap
    return cap