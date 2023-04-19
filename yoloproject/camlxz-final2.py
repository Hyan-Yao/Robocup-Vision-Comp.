import sys
from datetime import time

from PyQt5.QtCore import QThread, QMutex, pyqtSignal

from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
from camlxz import Ui_Form
import cv2

from sort_predict import mot_tracker
from track import SortBox, sort_and_draw_csv, Sort
from yolo import YOLO
import numpy as np
from PIL import Image
import copy

global ui, isCameraOpen, cap, isEnd, yolo, results, display, mot_tracker, isDetect, IMGS
isEnd = False
yolo = YOLO()
results = []
display = {}
mot_tracker = Sort()
frame_h = 480
frame_w = 640
isCameraOpen = False
isDetect = True
IMGS = []



class Ui_MainWindow(QMainWindow,Ui_Form):
    def __init__(self,parent=None,bufflen = 5):
        global IMGS
        IMGS = []
        super(Ui_MainWindow,self).__init__(parent)
        # self.timer_camera = QtCore.QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture()  # 视频流
        self.imgs = []  # 视频缓冲区，存放视频5帧缓存
        self.buff = bufflen

        self.CAM_NUM = 0 # 为0时表示视频流来自笔记本内置摄像头

        self.setupUi(self)  # 初始化程序界面
        self.detectThread = Mythread2()

        self.CallBackFunctions()  # 初始化槽函数
        # self.mythread = Mythread()
        # self.mythread.imgsignal.connect(self.show_img)
        self.i = 0



    def PrepSliders(self):
        self.button_open_camera.setEnabled(False)
        self.timer_camera.setEnabled(False)
        self.button_close.setEnabled(False)


    '''初始化所有槽函数'''

    def CallBackFunctions(self):
        self.button_open_camera.clicked.connect(self.button_open_camera_clicked)  # 若该按键被点击，则调用button_open_camera_clicked()
        # self.timer_camera.timeout.connect(self.show_camera)  # 若定时器结束，则调用show_camera()
        self.button_close.clicked.connect(self.close)  # 若该按键被点击，则调用close()，注意这个close是父类QtWidgets.QWidget自带的，会关闭程序


    def button_open_camera_clicked(self):
        self.detectThread.Send_signal.connect(self.Display)
        self.detectThread.signal_displaycount.connect(self.Displaycount)
        self.detectThread.start()
        QApplication.processEvents()

    def Display(self,img):

        self.show = cv2.resize(img, (640, 480))
        # self.show = cv2.cvtColor(self.show, cv2.COLOR_BGR2RGB)
        self.showImage = QtGui.QImage(self.show.data, self.show.shape[1], \
                                      self.show.shape[0], QtGui.QImage.Format_RGB888)
        self.label.setPixmap(QtGui.QPixmap.fromImage(self.showImage))

    def Displaycount(self, ress):

        print(ress)
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


class Mythread(QThread):
    imgsignal = QtCore.pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        # qmut2.lock()
        while 1:
            print("4111")
            if len(IMGS) >= 5:
                print("im in yolo now")
                frame = IMGS.pop(0)
                r_image = yolo.detect_image(frame)
                showImage = QtGui.QImage(r_image, 640, 480,
                                         QtGui.QImage.Format_RGB888)
                self.imgsignal.emit(showImage)
                # frame = IMGS.pop(0)
                # bboxes = yolo.get_bbox(frame)
                # print(bboxes)
                # if bboxes == [None]:
                #     image = np.asarray(frame)
                #     print("no image bbox")
                #
                # else:
                #     sort_boxes = []
                #
                #     for box in bboxes:
                #         sort_box = SortBox(box, yolo.class_names)
                #         sort_boxes.append(sort_box)
                #
                #         frame = np.asarray(frame)
                #         image, obs = sort_and_draw_csv(image=frame,
                #                                        boxes=sort_boxes,
                #                                        labels=yolo.class_names,
                #                                        obj_thresh=0.5,
                #                                        mot_tracker=mot_tracker)
                # im = Image.fromarray(image)
                # img_pix = im.toqpixmap().scaled(480 * 0.95, 360 * 0.95)
            else:
                continue

class Mythread2(QThread):
    Send_signal = pyqtSignal(object)
    signal_displaycount = pyqtSignal(object)
    def __init__(self):
        super(Mythread2, self).__init__()
        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, 640)
        self.capture.set(4, 480)
        self.fps = 0.0


    def run(self):
        ret, self.frame = self.capture.read()
        while ret:
            if isDetect:
                ret, self.frame = self.capture.read()
                self.drawPre(self.frame)


            else:
                ret, self.frame = self.capture.read()
                self.Send_signal.emit(self.frame)

            # self.drawPre(self.frame)


    def drawPre(self, frame):

        # image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        # image = Image.fromarray(image)
        # bbox = yolo.detect_image(image)
        # if bbox:
        #     print("success")
        # else:
        #     print("no bounding box")
        # image = np.asarray(image)
        # bbox = np.asarray(bbox)
        # print(type(bbox))
        # self.Send_signal.emit(bbox)
        # return image


        results = []
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(np.uint8(frame))
        print("wrong type")
        bboxes = yolo.get_bbox(frame)
        # 追踪函数有误，待修改
        # if bboxes == [None]:
        #     image = np.asarray(frame)
        # else:
        #     sort_boxes = []
        #     for box in bboxes:
        #         sort_box = SortBox(box, yolo.class_names)
        #         sort_boxes.append(sort_box)
        #
        #         frame = np.asarray(frame)
        #         image, obs = sort_and_draw_csv(image=frame,
        #                                        boxes=sort_boxes,
        #                                        labels=yolo.class_names,
        #                                        obj_thresh=0.5,
        #                                        mot_tracker=mot_tracker)
        #     if results == []:
        #         results = copy.deepcopy(obs)
        #     else:
        #         for ob in obs[::-1]:
        #             if ob[0] > results[0][0]:
        #                 results.insert(0, ob)
        #
        # res = count(results)

        # fps = (self.fps + (1. / (time.time() - t1))) / 2
        # print("fps= %.2f" % (fps))
        res = {'Unknown': 6, 'CD002': 3, 'CC002': 3, 'CC001': 3, 'CB002': 1}

        print(bboxes)
        frame =np.asarray(frame)

        self.Send_signal.emit(frame)
        self.signal_displaycount.emit(res)



def count(list):
    for i in list:
        if i[1] in display.keys():
            display[i[1]] = int(display[i[1]]) + 1
        else:
            display[i[1]] = 1
    return display


if __name__ == '__main__':

    app= QApplication(sys.argv)
    mywin = Ui_MainWindow()  # 实例化一个窗口小部件
    mywin.setWindowTitle('Hello world!')  # 设置窗口标题
    mywin.show()  # 显示窗口

    # thread = Mythread()
    # thread.start()
    sys.exit(app.exec_())