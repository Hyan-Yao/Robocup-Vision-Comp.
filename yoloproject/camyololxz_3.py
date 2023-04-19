import pickle
import sys
import threading
from socket import socket, AF_INET, SOCK_STREAM
import pyrealsense2 as rs
import imutils
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, QMutex, pyqtSignal
import time
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets

from TCP import Protocol
from camlxz2 import Ui_Form
import cv2
import matplotlib.animation as ani

# from sort_predict import mot_tracker
# from track import SortBox, sort_and_draw_csv, Sort
from yolo2 import YOLO
import numpy as np
from PIL import Image
import copy

global ui, isCameraOpen, cap, isEnd, yolo, results, display, mot_tracker, isDetect, IMGS
isEnd = False
yolo = YOLO()
results = []
display = {}
# mot_tracker = Sort()
frame_h = 480
frame_w = 640
isCameraOpen = False
#遮挡图片
coverpic_path="ratio62.jpg"
#black pic

blackpic_path="blackpic.jpg"
IMGS = []
SETNAME = set()
isDetect = True
dictres= {}

#裁判盒ip
server_ip = '192.168.1.100'
server_port = 6666

# 请勿修改该类型
DataType_IDSEND = 0
DataType_3D = 1


RESTRICT_NUM=2   #限制每类最大数量
ROUND = 2        #轮次参数

# 摄像头初始化

pipeline = rs.pipeline()
config = rs.config()
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

# 摄像头参数设定
config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
rs.option.brightness = 1000
rs.option.hue = 500

print(rs.option.brightness)



pf = pipeline.start(config)
sensor = pipeline.get_active_profile().get_device().query_sensors()[1]
print(sensor.get_supported_options())
frames = pipeline.wait_for_frames()



class Ui_MainWindow(QMainWindow,Ui_Form):
    def __init__(self,parent=None,bufflen = 5):
        global IMGS
        IMGS = []
        super(Ui_MainWindow,self).__init__(parent)
        self.timer_camera = QtCore.QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture()  # 视频流
        self.imgs = []  # 视频缓冲区，存放视频5帧缓存
        self.buff = bufflen
        self.fps = 0
        self.CAM_NUM = 0 # 为0时表示视频流来自笔记本内置摄像头

        self.setupUi(self)  # 初始化程序界面
        self.detectThread = Mythread2()

        self.CallBackFunctions()  # 初始化槽函数
        # self.mythread = Mythread()
        # self.mythread.imgsignal.connect(self.show_img)
        self.i = 0



    def PrepSliders(self):
        self.button_open_camera.setEnabled(False)
        self.button_close.setEnabled(False)


    '''初始化所有槽函数'''

    def CallBackFunctions(self):
        self.button_open_camera.clicked.connect(self.button_open_camera_clicked)  # 若该按键被点击，则调用button_open_camera_clicked()
        self.timer_camera.timeout.connect(self.DisplayImg)  # 若定时器结束，则调用show_camera()
        self.button_close.clicked.connect(self.TXTSAVE)  # 若该按键被点击，则调用close()，注意这个close是父类QtWidgets.QWidget自带的，会关闭程序



    def button_open_camera_clicked(self):
        self.detectThread.Send_signal.connect(self.Display)
        self.detectThread.signal_displaycount.connect(self.Displaycount)
        self.detectThread.Turn_signal.connect(self.DisplayImg)
        self.detectThread.start()
        QApplication.processEvents()


    def STOP(self):

        global isDetect,dictres
        print(isDetect)
        isDetect =not isDetect




    def Display(self,img):

        self.show = cv2.resize(img, (640, 480))
        # self.show = cv2.cvtColor(self.show, cv2.COLOR_BGR2RGB)
        self.showImage = QtGui.QImage(self.show.data, self.show.shape[1], \
                                      self.show.shape[0], QtGui.QImage.Format_RGB888)
        self.label.setPixmap(QtGui.QPixmap.fromImage(self.showImage))

    def Displaycount(self, ress):
        self.tableWidget.setRowCount(0)
        self.tableWidget.clearContents()
        for res in zip(ress.keys(), ress.values()):

            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            j = 0
            for tx in res:
                item = QTableWidgetItem(str(tx))
                self.tableWidget.setItem(row, j, item)
                j=j+1

    def DisplayImg(self, CHOICE):  # 显示转动图片
        if CHOICE:
            self.TURNING.setPixmap(QPixmap("./img/turn.png"))
        else:
            self.TURNING.setPixmap(QPixmap(" "))  #清除图片

    def TXTSAVE(self):
        global dictres
        with open('result.txt', "r+") as f:
            old = f.read()
            f.seek(0)
            f.write("START")
            f.write('\r')
            f.write('\r')
            f.write(old)

        for item in dictres.items():
            name = item[0]
            num = item[1]
            with open(r'result.txt', 'a') as f:
                f.write("Goal_ID=" + str(name) + ";" + "Num=" + str(num))
                f.write('\r')

        with open('result.txt', "a+") as f:
            f.write("END")



    def show_camera(self):

        flag, self.image = self.cap.read()  # 从视频流中读取
        self.i=self.i+1
        if flag:
            self.imgs.append(self.image)
            IMGS.append(self.image)
            self.update()
        buff_len= len(self.imgs)

        if(buff_len>self.buff):
            self.imgs=self.imgs[-self.buff:]
        if(buff_len<self.buff):
            self.timer_camera.stop()
            flag, self.image = self.cap.read()
            if flag:
                self.imgs.append(self.image)
                IMGS.append(self.image)
            self.timer_camera.start(30)

        if(len(IMGS)>=self.buff):
            IMGS.pop(0)
        if self.imgs:
            data=self.imgs.pop(0)

            # r_image = yolo.detect_image(data)
            # r_image = yolo.detect_image(data)

            show = cv2.resize(data, (640, 480))  # 把读到的帧的大小重新设置为 640x480
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色

            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                     QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.label.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage



class Mythread2(QThread):

    Send_signal = pyqtSignal(object)
    signal_displaycount = pyqtSignal(object)
    dict_signal = pyqtSignal(object)
    Turn_signal = pyqtSignal(object)

    def __init__(self):
        super(Mythread2, self).__init__()
        self.capture = cv2.VideoCapture("19sroll.mp4")
        self.capture.set(3, 1280)
        self.capture.set(4, 720)
        self.fps = 0.0
        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.c = 1
        self.frameRate = 10
        (self.W, self.H) = (None, None)
        self.kinetic = False
        self.fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
        self.kinetic_count = 0
        self.max_count = 5
        self.frames_n = 0
        self.min_per = 4
        self.max_per = 30
        self.warmup = 10


    def run(self):
        global isDetect
        # ret, self.frame = self.capture.read()

        # print(type(self.frame))
        # print("begin")
        # image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        # img2 = image
        # image = Image.fromarray(np.uint8(image))
        # yolo.detect_image(image)
        # print("end")

        # self.client_th = threading.Thread(target=self.TCPconnect(0))
        # self.client_th.setDaemon(True)
        # self.client_th.start()

        realround = 1

        id = 0

        while realround <= ROUND:

            if realround == 1:
                isDetect = True
                t1 = time.perf_counter()

                while True:
                    # opencv调用摄像头
                    # ret, self.frame = self.capture.read()

                    # 通过realsense调用摄像头
                    frames = pipeline.wait_for_frames()
                    color_frame = frames.get_color_frame()
                    color_image = np.asanyarray(color_frame.get_data())
                    timestart = time.perf_counter()
                    t2 = time.perf_counter()

                    if id == 1:
                        self.client_th = threading.Thread(target=self.TCPconnect(0))
                        self.client_th.setDaemon(True)
                        self.client_th.start()
                        id = id + 1

                    if isDetect:
                        if t2 - t1 < 10:
                            # self.drawPre(self.frame)
                            self.drawPre(color_image, False)
                            timeend = time.perf_counter()
                            id = id + 1
                            print(1.0/(timeend-timestart))
                            fps = 1.0/(timeend-timestart)
                        else:
                            print("15s结束")
                            self.SaveTxt(dictres)
                            self.SaveTxtCopy(dictres)

                            self.client_th = threading.Thread(target=self.TCPconnect(1))
                            self.client_th.setDaemon(True)
                            self.client_th.start()

                            # self.DelTxt()
                            isDetect = False
                    else:

                        print("不显示图片")
                        realround = realround+1
                        break




            # self.drawPre(self.frame)
    def Kneticjud(self):

        pic = cv2.imread(coverpic_path)
        color_image1 = np.array(self.frame * pic, dtype=np.uint8)
        color_image2 = imutils.resize(color_image1, width=600)
        mask = self.fgbg.apply(color_image2)

        # apply a series of erosions and dilations to eliminate noise
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        if self.W is None or self.H is None:
            (self.H, self.W) = mask.shape[:2]
            # compute the percentage of the mask that is "foreground"
        p = (cv2.countNonZero(mask) / float(self.W * self.H)) * 100
        if p < self.min_per and self.kinetic and self.frames_n > self.warmup:
            # silent
            self.kinetic_count += 1
            if self.kinetic_count > self.max_count:
                self.kinetic = False
                self.kinetic_count = 0
                isDetect = True
                print("Silent now")
                print("等待转动，当前静止中")
        elif p > self.max_per and not self.kinetic:
            self.kinetic_count += 1
            if self.kinetic_count > self.max_count:
                self.kinetic = True
                self.kinetic_count = 0
                isDetect = False
                print("Kinetic now")
                print("转动中")
        self.frames_n += 1

    def drawPre(self, frame, choice):

        global dictres

        image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        image = Image.fromarray(np.uint8(image))

        box = (100, 50, 1500, 1400)
        region = image.crop(box)
        bbox, labels = yolo.detect_image(region, choice)
        if bbox:
            print("------------")
        else:
            print("no bounding box")
        image.paste(bbox, box)
        newpic = np.asarray(image)
        bbox = np.asarray(bbox)
        if labels:
            dict = {}
            for key in labels:
                key = key.decode()
                key = key.split()
                if len(SETNAME)==0:
                    globals()[str(key[0])] = set()
                else:

                    if key[0] in SETNAME:
                        continue
                    else:
                        globals()[str(key[0])] = set()
                SETNAME.add(key[0])

            for key in labels:
                key = key.decode()
                key = key.split()
                globals()[str(key[0])].add(key[1])

                # dict[key[0]] = len(globals()[str(key[0])])
            for name in SETNAME:
                # if dict[name] <= RESTRICT_NUM:
                dict[name] = len(globals()[str(name)])

            # 数量限制
            for name in SETNAME:
                if dict[name] >= RESTRICT_NUM:
                    dict[name] = RESTRICT_NUM

            print(dict)
            dictres = dict
            self.signal_displaycount.emit(dict) # dict应为字典类的label数据，如下面的res格式
        else:
            dict = { }
        res = {'Unknown': 6, 'CD002': 3, 'CC002': 3, 'CC001': 3, 'CB002': 1}
        self.Send_signal.emit(newpic)




    def TCPconnect(self,i):
        if i==0:
            p1 = Protocol()
            p1.add_str("xjtu")
            p1 = p1.get_pck_has_head(DataType_IDSEND)
            tcp_client_socket = socket(AF_INET, SOCK_STREAM)
            tcp_client_socket.connect((server_ip, server_port))
            tcp_client_socket.send(p1)
            print("lets go")
            tcp_client_socket.close()
        else:
            p = Protocol()
            with open('result.txt', "r") as f:
                for line in f:
                    p.add_str(line)
            p = p.get_pck_has_head(DataType_3D)

            tcp_client_socket2 = socket(AF_INET, SOCK_STREAM)
            tcp_client_socket2.connect((server_ip, server_port))
            tcp_client_socket2.send(p)
            print("lets go")
            tcp_client_socket2.close()


    def SaveTxt(self, dict):
        global isDetect
        # 将dict存到result里面
        with open('result.txt', "r+") as f:
            old = f.read()
            f.seek(0)
            f.write("START")
            f.write('\r')
            f.write(old)

        for item in dict.items():
            name = item[0]
            num = item[1]
            with open(r'result.txt', 'a') as f:
                f.write("Goal_ID=" + str(name) + ";" + "Num=" + str(num))
                f.write('\r')

        with open('result.txt', "a+") as f:
            f.write("END")

    def SaveTxtCopy(self, dict):
        global isDetect
        # 将dict存到result里面
        with open('result_copy.txt', "a+") as f:
            f.write("START")
            f.write('\r')

        for item in dict.items():
            name = item[0]
            num = item[1]
            with open(r'result_copy.txt', 'a') as f:
                f.write("Goal_ID=" + str(name) + ";" + "Num=" + str(num))
                f.write('\r')

        with open('result_copy.txt', "a+") as f:
            f.write("END")
            f.write("\r")

    def DelTxt(self):
        global isDetect
        # 将dict存到result里面
        with open('result.txt', "r+") as f:
          f.truncate(0)


    def count(list):
        for i in list:
            if i[1] in display.keys():
                display[i[1]] = int(display[i[1]]) + 1
            else:
                display[i[1]] = 1
        return display

    def countlist(list):
        set = set(list)
        dict = {}
        for item in set:
            dict.update({item: list.count(item)})
        print(dict)
        return dict

if __name__ == '__main__':

    app= QApplication(sys.argv)
    mywin = Ui_MainWindow()  # 实例化一个窗口小部件
    mywin.setWindowTitle('目标识别')  # 设置窗口标题
    mywin.show()  # 显示窗口

    # thread = Mythread()
    # thread.start()
    sys.exit(app.exec_())