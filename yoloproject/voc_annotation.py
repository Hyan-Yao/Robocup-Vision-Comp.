import  xml.dom.minidom

from os import getcwd

import numpy as np

def parser_for_xml(path):


    dom = xml.dom.minidom.parse(path)

    data = dom.documentElement

    objects = data.getElementsByTagName('object')
    ans = []
    for object in objects:
        cls = object.getElementsByTagName("name")[0].childNodes[0].nodeValue
        cls = str(cls)
        if ("_"in cls):
            num=cls.split("_")
            try:
                id=eval(num[-1])
            except:
                id=-1
        else:
             id=-1

        cls = (ord(cls[1]) - 65)*4 + ord(cls[4]) - ord('0')

        xmin = object.getElementsByTagName('xmin')[0].childNodes[0].nodeValue
        xmin = eval(xmin)
        xmax = object.getElementsByTagName('xmax')[0].childNodes[0].nodeValue
        xmax = eval(xmax)
        ymin = object.getElementsByTagName('ymin')[0].childNodes[0].nodeValue
        ymin = eval(ymin)
        ymax = object.getElementsByTagName('ymax')[0].childNodes[0].nodeValue
        ymax = eval(ymax)
        ans.append([cls,id, xmin, ymin, xmax, ymax])
    ans = np.array(ans,'float32')

    return ans

sets=[('2007', 'train'), ('2007', 'val'), ('2007', 'test')]

wd = getcwd()
#classes = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
# classes = ["CA001","CA002","CA003","CA004","CD001","CD002","CD003","CD004","CD005","CD006","ZA001","ZA002","ZA003","ZA004","ZA005","ZA006","ZB001","ZB002","ZB003","ZB004","ZB005","ZB006","ZB007","ZB008","ZB009","ZB010","ZC001","ZC002","ZC003","ZC004","ZC005","ZC006","ZC007","ZC008","ZC009","ZC010","ZC011","ZC012","ZC013","ZC014","ZC015","ZC016","ZC017","ZC018","ZC019","ZC020","ZC021","ZC022","ZC023","tag"]
classes = ["battery", "ZC012", "ZC017", "ZC016", "ZC009", "ZB006", "ZC011", "ZB008", "ZA006", "ZB005"]
max_id=0
def convert_annotation(year, image_id, list_file):
    try:
        in_file = open(image_id+'.xml')
        img=image_id
        list_file.write(img.replace('ann','img')+'.jpg')
        listt=parser_for_xml(in_file)
        for object in listt:
            cls_id,id, xmin, ymin, xmax, ymax=object
            b = (int(xmin), int(ymin), int(xmax), int(ymax))
            list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(int(cls_id-1)))
    except:
        pass
    list_file.write('\n')

for year, image_set in sets:






    image_ids = open(r'E:\lyh\yolov4-tiny-pytorch-master\yolov4-tiny-pytorch-master\VOCdevkit\VOC2007\%s.txt'%(image_set)).read().strip().split()
    list_file = open('%s_%s.txt'%(year, image_set), 'w')
    for image_id in image_ids:

        try:
            convert_annotation(year, image_id, list_file)

        except:
            print(image_id)
    list_file.close()
