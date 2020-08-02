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
import math
import touchSocket

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

#计算两点间距离
def getDistance(v1,v2):
    dis = math.sqrt(math.pow(v1[0]-v2[0],2) + math.pow(v1[1]-v2[1],2))
    return int(dis)
   

#所有锚点的坐标偏移都为x方向为宽度一半,y方向上:f和c为向下半个宽度,r为向上半个宽度,s的x,y为w,h的一半

msPerDistence = 1.8  #每个像素坐表示多常时间的毫秒延时

def getTouchTimeDelay(boxes):
    rbox = {}       #跳一跳小人坐标盒子
    fboxes = []     #所有方块的坐标盒子
    # cbox = []       #所有圆型块坐标盒子
    sbox = {}       #开始游戏坐标盒子
    for i,v in boxes.items():
        # v={'x':x,'y':y,'w':w,'h':h,'t':self.LABELS[classIDs[i]],'s':confidences[i]}
        if v['t'] == 'r':
            Px = int(v['x'] + v['w']/2.0)
            Py = int(v['y'] + (v['h'] - v['w']/2.0))
            rbox = v
            rbox['p'] = [Px,Py]
        elif v['t'] == 'f':
            Px = int(v['x'] + v['w']/2.0)
            Py = int(v['y'] + v['w']/2.0)
            tmpv = v
            tmpv['p'] = [Px,Py]
            fboxes.append(tmpv)
        elif v['t'] == 'c':
            Px = int(v['x'] + v['w']/2.0)
            Py = int(v['y'] + v['w']/2.0)
            tmpv = v
            tmpv['p'] = [Px,Py]
            fboxes.append(tmpv)
        elif v['t'] == 's':
            Px = int(v['x'] + v['w']/2.0)
            Py = int(v['y'] + v['h']/2.0)
            sbox = v
            sbox['p'] = [Px,Py]
        else:
            print('fand type erro....')
            return -2
    #计算所有块与小人距离,以及下一个人跳到的块是那一个
    nextBox = 0
    nextdis = 0
    minPy = 10000
    mindis = 10000
    rindex = 0
    if sbox:
        print('is start UI...')
        return -1
    for i,v in enumerate(fboxes):
        dis = getDistance((v['p']), rbox['p'])
        if dis <= mindis:
            rindex = i
            mindis = dis
        if v['p'][1] < rbox['p'][1]:
            tmppy = rbox['p'][1] - v['p'][1]
            if tmppy < minPy:
                minPy = tmppy
                nextBox = i
                nextdis = dis
    print(rbox['p'],fboxes[rindex]['p'],fboxes[nextBox]['p'],nextdis)
    #计算距离转换为延时间
    dtime = int(nextdis*msPerDistence)
    print('delytime:%d'%(dtime))
    return dtime

def main():
    touchclient = touchSocket.ClientSocket('192.168.0.193')

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
            getTouchTimeDelay(boxes)
        elif 0xFF & cv2.waitKey(0) == ord('q'):
            break
    

if __name__ == '__main__':
    main()

