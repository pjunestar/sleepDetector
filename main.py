import cv2
import dlib
from math import hypot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
from sleepDetectionGUI import Ui_MainWindow
import threading


END = False
class UI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

    def startchk(self):
        th = thread1()
        th.start()

    def stopchk(self):
        global a
        global END
        END = True
        self.imageLabel.clear()


app = QApplication([])

def midpoint(p1, p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)


def get_blinking_ratio(eye_points, facial_landmarks):                               #눈 가로 길이/세로 길이
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
    return ratio 
    

detector = dlib.get_frontal_face_detector()                                         # create default face detector
predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")
font = cv2.FONT_HERSHEY_SIMPLEX
r_eye_points = [42, 43, 44, 45, 46, 47]
l_eye_poits = [36, 37, 38, 39, 40, 41]
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)                                          #영상 크롭
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 

cnt = 0

class thread1(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        

    def run(self):
        global a
        global cnt
        i = 0
        while not END:                                                              #while 돌면서 눈의 가로 길이가 세로 길이의 6배 이상이 
                                                                                    #되면 눈을 감은것으로 카운팅
            ret, img = capture.read()
            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                h,w,c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                a.imageLabel.setPixmap(pixmap)

            faces = detector(img)

            for face in faces:
                landmarks = predictor(img, face)

                left_eye_ratio = get_blinking_ratio(l_eye_poits, landmarks)
                right_eye_ratio = get_blinking_ratio(r_eye_points, landmarks)
                blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

                if blinking_ratio >= 6.0:
                    cnt += 1     
                    if cnt > 3 : print("sleeping", cnt-3)                                        #눈 감은것 감지되면 시간 측정 시작

                else:
                    cnt = 0  


            if cnt > 15:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) 
                cv2.imwrite("imageFolder\\Sleeping student(%d).png" %i, img)        #10초이상 눈 감은 상태가 지속될 경우 이미지 저장하고 시간 초기화
                cnt = 0
                i += 1



a=UI()
sys.exit(app.exec_())