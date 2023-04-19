import os
import random 
random.seed(0)
dataset_path=r"E:\3d_detector\Data2021\MIX"
xmlfilepath=[]
saveBasePath=r"E:\lyh\yolov4-tiny-pytorch-master\yolov4-tiny-pytorch-master\VOCdevkit\VOC2007"
 
trainval_percent=0.9
train_percent=0.3

dataset = os.listdir(dataset_path)
total_xml = []
for kind in dataset:
    xmlfilepath.append(kind+r'\ann')


for path in xmlfilepath:
    try:
        xml=os.listdir(dataset_path+'\\'+path)
        for file in xml:
            if file.endswith(".xml"):
                total_xml.append(dataset_path+'\\'+path+'\\'+file)
    except:
        pass

num=len(total_xml)
print(num)
list=range(num)  
tv=int(num*trainval_percent)  
tr=int(tv*train_percent)
trainval= random.sample(list,tv)
train=random.sample(list,tr)
 
print("train and val size",tv)
print("traub suze",tr)
ftrainval = open(os.path.join(saveBasePath,'trainval.txt'), 'w')  
ftest = open(os.path.join(saveBasePath,'test.txt'), 'w')
ftrain = open(os.path.join(saveBasePath,'train.txt'), 'w')  
fval = open(os.path.join(saveBasePath,'val.txt'), 'w')  
 
for i  in list:  
    name=total_xml[i][:-4]+'\n'
    if i in trainval:  
        ftrain.write(name)
        if i in train:  
            ftrainval.write(name)
        else:  
            fval.write(name)  
    else:  
        ftest.write(name)  
  
ftrainval.close()  
ftrain.close()  
fval.close()  
ftest .close()
