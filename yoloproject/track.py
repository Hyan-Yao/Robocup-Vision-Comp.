import cv2
import matplotlib.pyplot as plt
import numpy as np


def crop_detection(img,bbox):
    xmin,ymin,xmax,ymax=bbox
    img = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
    dst = img[ymin:ymax, xmin:xmax]   # 裁剪坐标为[y0:y1, x0:x1]
    return dst

def hist(dst):
    color = ['b','g','r']
    hst_all=[]
    for i,col in enumerate(color):
        hst = cv2.calcHist([dst], [i], None, [256], [0, 255])
        hst_all.append(hst)
        #plt.plot(hst)
        #plt.xlim([0, 255])
        #plt.show()
    return hst_all



class assign:
    def __init__(self,class_names,classes=17,ths=40000):
        self.all={}
        self.ths=ths
        for i in range(classes):
            self.all[i]=list()
        self.class_names=class_names
    def add(self,cls,mat):
        comp_t=self.all[cls]
        maxx=0
        for t in list(comp_t):
            try:
                maxx=max(maxx,self.comp(mat,t))
            except:
                maxx=0
        if maxx>self.ths or len(list(comp_t))<=0:
            self.all[cls].append(mat)
            print(f"New id! CLS {self.class_names[int(cls)]} NUM{len(self.all[cls])} MAXX {maxx}")
    def comp(self,dst1,dst2,ord=2):
        return np.linalg.norm(dst2-dst1, ord, axis=None, keepdims=False)

    def update(self,detections,image):
        '''

        :param detections:{numpy.ndarray} - in the format [[x1, y1, x2, y2, score], [x1, y1, x2, y2, score], ...]
                image:cv2.image
        :return: None
        '''
        for detect in detections:
            bbox=detect[:4]
            bbox=[int(i) for i in bbox]
            cls=int(detect[-1])
            img=crop_detection(image,bbox)
            a,_,_=hist(img)
            self.add(cls,a)

    
        



if __name__ == '__main__':
    img='test.jpg'
    dst=crop_detection(img,[0,0,300,600])
    a,b,c=hist(dst)
    ass=assign()
    ass.add(1,a)
    print(comp(np.array(a),np.array(b)))