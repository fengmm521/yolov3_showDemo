#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-08-01 11:28:48
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os,sys
from PIL import ImageGrab,Image, ImageTk
import numpy as np 
import cv2
import gameyolo
import json
import time
from magetool import pathtool

#从本地读取一张图片
def getCVImg(imgpth):
    im = Image.open(imgpth)
    pilimg=im.convert('RGB')
    cv2img = cv2.cvtColor(np.asarray(pilimg),cv2.COLOR_RGB2BGR)
    # img_np = np.array(img)
    return cv2img

# {'x':x,'y':y,'w':w,'h':h,'t':self.LABELS[classIDs[i]],'s':confidences[i]}
def showBox(box):
    for k,v in box.items():
        tmpv = {'p':[v['x'],v['y']],'size':[v['w'],v['h']],'t':v['t'],'s':v['s']}
        print(tmpv)

def conventBoxForXY(box):
    outdict = {}
    W = 0
    H = 0
    for k,v in box.items():
        if W == 0:
            W = v['imgW']
            H = v['imgH']
        minx = v['x']
        if minx < 0:
            minx = 0
        miny = v['y']
        if miny < 0:
            miny = 0
        maxx = v['x'] + v['w']
        if maxx > W:
            maxx = W
        maxy = v['y'] + v['h']
        if maxy > H:
            maxy = H
        #分别改换为坐标和置信度
        isTru = 0
        if v['x'] <= 0 or v['y'] <=0 or v['x'] >= W or v['y'] >= H:
            isTru = 1
        outdict[k] = {'minx':minx,'miny':miny,'maxx':maxx,'maxy':maxy,'class':v['t'],'pencert':v['s'],'tc':isTru}
    return outdict,W,H

#加载YOLO模型数据
def getYOLONet():
    labelsPath = os.getcwd() + os.sep +'yolo-net' +os.sep + 'my.names'
    weightsPath = os.getcwd() + os.sep +'yolo-net'+ os.sep + "yolov3.weights"
    configPath = os.getcwd() + os.sep +'yolo-net' + os.sep + "yolov3.cfg"
    yolonet = gameyolo.YOLONet(weightsPath, configPath, labelsPath)
    return yolonet

#获取一张图片的识别结果
def getObjects(yolonet,image):
    oimg,boxdict = yolonet.fandObjects(image)
    # roimg = resizeImg(oimg)
    # showImg(roimg)
    # {'x':x,'y':y,'w':w,'h':h,'t':self.LABELS[classIDs[i]],'s':confidences[i]}
    return boxdict,oimg

def getFileNameFromPath(fpth):
    tmp = fpth.split('/')[-1]
    fname = tmp.split('.')[0]
    return fname

def getFileNameAndFolder(fpth):
    tmps = fpth.split('/')
    fname = tmps[-1]
    folder = tmps[-2]
    return fname,folder

#获取一张图片的xml标注文件
def getImgXmlFloagFile(yolonet,imgpth,savePth):
    cv2img = getCVImg(imgpth)
    boxdict,oimg = getObjects(yolonet, cv2img)
    mmbix,W,H = conventBoxForXY(boxdict)
    print(boxdict)
    fname,folder = getFileNameAndFolder(savePth)
    outxml = '''<annotation verified="yes">
    <folder>%s</folder>
    <filename>%s</filename>
    <path>%s</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>%d</width>
        <height>%d</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    '''%(folder,fname,savePth,W,H)
    for k,v in mmbix.items():
        outxml += '''<object>
        <name>%s</name>
        <pose>Unspecified</pose>
        <truncated>%d</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>%d</xmin>
            <ymin>%d</ymin>
            <xmax>%d</xmax>
            <ymax>%d</ymax>
        </bndbox>
    </object>
    '''%(v['class'],v['tc'],v['minx'],v['miny'],v['maxx'],v['maxy'])
    outxml += '''</annotation>
'''
    return outxml

def saveStrToFile(pth,data):
    f = open(pth,'w')
    f.write(data)
    f.close()

def copyfile(spth,tpth):
    f = open(spth,'rb')
    dat = f.read()
    f.close()
    f = open(tpth,'wb')
    f.write(dat)
    f.close()

def saveHandXmlName(fname,fxmlpth,outpth):
    f = open(outpth,'a')
    ostr = fname + ',' + fxmlpth + '\n'
    f.write(ostr)
    f.close()

def main():
    yolonet = getYOLONet()
    imgDirpth = '/Volumes/mage/res/taobao/labelimg/flogdata/tb_chenbo/20200911'
    # imgDirpth = '/Volumes/mage/res/taobao/labelimg/flogdata/tb_chenbo/autoimg'
    outdirpth = '/Volumes/mage/res/taobao/labelimg/flogdata/tb_chenbo/out'
    handpth = '/Volumes/mage/res/taobao/labelimg/flogdata/tb_chenbo/handout'
    outxmlhpth = '/Volumes/mage/res/taobao/labelimg/flogdata/tb_chenbo/hand.csv'
    imgs = pathtool.getAllFiles(imgDirpth,'.png')
    for i,v in enumerate(imgs):
        ipth = imgDirpth + v
        print(ipth)
        fname = getFileNameFromPath(ipth)
        fxmlpth = imgDirpth + os.sep + fname + '.xml'
        xmlsavepth = outdirpth + os.sep + fname + '.xml'
        saveimgpth = outdirpth + v
        if os.path.exists(fxmlpth):
            saveHandXmlName(fname, fxmlpth, outxmlhpth)
            hsavexmlpth = handpth + os.sep + fname + '.xml'
            hsaveimgpth = handpth + v
            copyfile(fxmlpth, hsavexmlpth)
            copyfile(ipth, hsaveimgpth)
            continue
        if os.path.exists(xmlsavepth):
            print(xmlsavepth)
            continue
        xmlstr = getImgXmlFloagFile(yolonet,ipth,saveimgpth)
        saveStrToFile(xmlsavepth, xmlstr)
        copyfile(ipth, saveimgpth)
        print('index=%d'%(i))
        time.sleep(0.2)
    

if __name__ == '__main__':
    main()

