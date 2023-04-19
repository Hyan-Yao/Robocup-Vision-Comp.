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
from yolo import YOLO
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
server_ip = '192.168.0.179'
server_port = 6666

# 请勿修改该类型
DataType_IDSEND = 0
DataType_3D = 1

p1 = Protocol()
p1.add_str("xjtu")
p1 = p1.get_pck_has_head(DataType_IDSEND)
tcp_client_socket = socket(AF_INET, SOCK_STREAM)
tcp_client_socket.connect((server_ip, server_port))

tcp_client_socket.send(p1)
print("lets go")
tcp_client_socket.close()


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