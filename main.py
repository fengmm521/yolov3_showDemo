#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-08-01 11:28:48
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os,sys
from PIL import ImageGrab
import numpy as np 
import cv2
import gameyolo
import json

#截取电脑屏图像
def capImg(box = (0,50,1100,1440)):
    
    img = ImageGrab.grab(bbox=box)#设置窗口大小
    img = img.convert('RGB')
    img_np = np.array(img)
    return img_np

#缩放图片
def resizeImg(img,scale = 0.45):
    w = int(img.shape[1]*scale)
    h = int(img.shape[0]*scale)
    rimg = cv2.resize(img, (w,h), interpolation = cv2.INTER_AREA)
    return rimg

#打开一个窗口显示图片
def showImg(img,winName = 'img'):
    cv2.imshow(winName,img)
    return winName

#移动窗口位置
def moveWindow(winName,x,y):
    cv2.moveWindow(winName,x,y)


def getObjects(yolonet,image):
    oimg,boxdict = yolonet.fandObjects(image)
    roimg = resizeImg(oimg)
    showImg(roimg)
    return boxdict


def main():
    labelsPath = os.getcwd() + os.sep +'yolo-net' +os.sep + 'my.names'
    weightsPath = os.getcwd() + os.sep +'yolo-net'+ os.sep + "yolov3.weights"
    configPath = os.getcwd() + os.sep +'yolo-net' + os.sep + "yolov3.cfg"
    yolonet = gameyolo.YOLONet(weightsPath, configPath, labelsPath)
    #左上角x,y,右下角x,y
    # box = (0,50,1100,1440)
    img = capImg()
    rimg = resizeImg(img)
    wName = showImg(rimg)
    moveWindow(wName, 600, 0)
    # isRun = True
    while True:
        #每输入一个空格时进行下一次截图并识别
        if 0xFF & cv2.waitKey(0) == ord(' '):  
            img = capImg()
            boxes = getObjects(yolonet, img)
            print(boxes)
        elif 0xFF & cv2.waitKey(0) == ord('q'):
            break
    

if __name__ == '__main__':
    main()

