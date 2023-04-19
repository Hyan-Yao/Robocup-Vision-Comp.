import sys

from PyQt5.QtCore import QThread, QMutex, pyqtSignal

from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
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
isDetect = False
IMGS = []
qmut1 = QMutex()
qmut2 = QMutex()


class Ui_MainWindow(QMainWindow,Ui_Form):
    def __init__(self,parent=None,bufflen = 5):
        global IMGS
        IMGS = []
        super(Ui_MainWindow,self).__init__(parent)
        self.timer_camera = QtCore.QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture()  # 视频流
        self.imgs = []  # 视频缓冲区，存放视频5帧缓存
        self.buff = bufflen

        self.CAM_NUM = 0 # 为0时表示视频流来自笔记本内置摄像头

        self.setupUi(self)  # 初始化程序界面

        self.CallBackFunctions()  # 初始化槽函数
        self.i = 0



    def PrepSliders(self):
        self.button_open_camera.setEnabled(False)
        self.timer_camera.setEnabled(False)
        self.button_close.setEnabled(False)


    '''初始化所有槽函数'''

    def CallBackFunctions(self):
        self.button_open_camera.clicked.connect(self.button_open_camera_clicked)  # 若该按键被点击，则调用button_open_camera_clicked()
        self.timer_camera.timeout.connect(self.show_camera)  # 若定时器结束，则调用show_camera()
        self.button_close.clicked.connect(self.close)  # 若该按键被点击，则调用close()，注意这个close是父类QtWidgets.QWidget自带的，会关闭程序


    def button_open_camera_clicked(self):

        self.mythread = Mythread()
        self.mythread.imgsignal.connect(self.show_img)
        self.mythread.start()

        if self.timer_camera.isActive() == False:  # 若定时器未启动
            flag = self.cap.open(self.CAM_NUM)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
            if flag == False:  # flag表示open()成不成功
                msg = QtWidgets.QMessageBox.warning(self, 'warning', "请检查相机于电脑是否连接正确", buttons=QtWidgets.QMessageBox.Ok)
            else:
                self.timer_camera.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
                self.button_open_camera.setText('关闭相机')
        else:
            self.timer_camera.stop()  # 关闭定时器
            self.cap.release()  # 释放视频流
            self.label.clear()  # 清空视频显示区域
            self.button_open_camera.setText('打开相机')

    def show_img(self, img):
        showImage = QtGui.QImage(img, 640, 480,
                                 QtGui.QImage.Format_RGB888)
        self.label.setPixmap(QtGui.QPixmap.fromImage(showImage))


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
        if len(IMGS) >= 6:
            IMGS.pop(0)

        # if self.imgs:
        #     data=self.imgs.pop(0)
        #     show = cv2.resize(data, (640, 480))  # 把读到的帧的大小重新设置为 640x480
        #     show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
        #
        #     showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
        #                              QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        #     self.label.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage


class Mythread(QThread):
    imgsignal = QtCore.pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)


    def run(self):
        # qmut2.lock()
        while 1:
            # self.mythread2 = Mythread2()
            print(len(IMGS))
            if len(IMGS) >= 5:
                print("im in yolo now")
                self.frame = IMGS.pop(0)  # 把读到的帧的大小重新设置为 640x480
                show = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
                # show = yolo.detect_image(self.frame)
                self.imgsignal.emit(show)


                # self.mythread2.Send_signal.connect(self.givemsg)
                # self.mythread2.start(self.frame)

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
                # img_pix = im.toqpixmap().scaled(480 * 0.95, 360 * 0.95

    def givemsg(self, img):
        self.imgsignal.emit(img)


# class Mythread2(QThread):
#     Send_signal = QtCore.pyqtSignal(object)
#
#     def __init__(self):
#         super(Mythread2, self).__init__()
#         self.capture = cv2.VideoCapture(0)
#         self.capture.set(3, 640)
#         self.capture.set(4, 480)
#         self.yolo= YOLO()
#
#
#     def run(self,frame):
#         self.drawPre(frame)
#
#
#     def drawPre(self, image):
#         # image  = yolo.detect_image(image)
#         image= cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#         print(type(image))
#         self.Send_signal.emit(image)
#
#         # return image
#



if __name__ == '__main__':

    app= QApplication(sys.argv)
    mywin = Ui_MainWindow()  # 实例化一个窗口小部件
    mywin.setWindowTitle('Hello world!')  # 设置窗口标题
    mywin.show()  # 显示窗口

    # thread = Mythread()
    # thread.start()
    sys.exit(app.exec_())