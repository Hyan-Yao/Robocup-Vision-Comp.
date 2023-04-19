from yolo import YOLO
import os
from PIL import Image
import cv2 as cv

yolo = YOLO()

while True:
    #测试某个文件夹中所有的图片
    # path = r"E:\\3d_detector\\Data2021\\MIX\\MIX001"
    # foldName = "./img"
    # imgs = os.listdir(path + foldName)
    # imgNum = len(imgs)
    # for i in range(imgNum):
    #     try:
    #         image = Image.open(path + foldName+"/"+imgs[i])
    #     except:
    #         print('Open Error! Try again!')
    #         continue
    #     else:
    #         r_image = yolo.detect_image(image)
    #         print(path + foldName +"/"+imgs[i])
    #         r_image.show()

    #正常打开
    # img  = input ('Input your image filename')
    # try:
    #     image = Image.open(img)
    # except:
    #     print('Open Error! Try again')
    #     continue
    # else:
    #     r_image = yolo.detect_image(image)
    #     r_image.show()

    #测试text中的例子
    with open('2007_test.txt','r') as f_read:
        for line in f_read:
            myIndex = line.index(' ')
            img = line[0:myIndex]
            #把所有的地址全部提取出来到test_address.txt
            with open("test_address.txt",'a' )as f_write:
                f_write.write(img)
            try:
                image = Image.open(img)
            except:
                print('Open Error! Try again')
                continue
            else:
                r_image = yolo.detect_image(image)
               # r_image.save('C:\Users\Administrator\Desktop\test_picture')
                r_image.show()