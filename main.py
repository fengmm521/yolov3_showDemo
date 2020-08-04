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
import math
import touchSocket
import time
from queue import Queue
import tkinter as tk
import threading
import tktool

#截取电脑屏图像
def capImg(box = (0,50,1100,1490)):
    
    img = ImageGrab.grab(bbox=box)#设置窗口大小
    pilimg = img.convert('RGB')
    cv2img = cv2.cvtColor(np.asarray(pilimg),cv2.COLOR_RGB2BGR)
    # img_np = np.array(img)
    return pilimg,cv2img

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
    # roimg = resizeImg(oimg)
    # showImg(roimg)
    return boxdict,oimg

#计算两点间距离
def getDistance(v1,v2):
    dis = math.sqrt(math.pow(v1[0]-v2[0],2) + math.pow(v1[1]-v2[1],2))
    return int(dis)
   

#所有锚点的坐标偏移都为x方向为宽度一半,y方向上:f和c为向下半个宽度,r为向上半个宽度,s的x,y为w,h的一半

msPerDistence = 1.47  #每个像素坐表示多常时间的毫秒延时

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
    try:
    # if True:
        for i,v in enumerate(fboxes):
            dis = getDistance((v['p']), rbox['p'])
            if dis <= mindis:
                rindex = i
                mindis = dis
        
        rfbox = fboxes.pop(rindex)
        for i,v in enumerate(fboxes):
            dis = getDistance((v['p']), rbox['p'])
            if v['p'][1] < rfbox['p'][1]:
                tmppy = rbox['p'][1] - v['p'][1]
                if tmppy < minPy:
                    minPy = tmppy
                    nextBox = i
                    nextdis = dis
        print(minPy,mindis,rindex,nextBox)
        # print(rbox['p'],fboxes[rindex]['p'],fboxes[nextBox]['p'],nextdis)
        #计算距离转换为延时间
        dtime = int(nextdis*msPerDistence)
        # if dtime > 800:
        #     dtime -=50
        print('delytime:%d'%(dtime))
        return dtime
    except Exception as e:
        print(e)
        print('getDistance erro...')

client = None


def setUnTouch():
    global client
    if client:
        client.send('1')

def delayTimeFunc(ptime):
    print(ptime)
    setUnTouch()

def intToHexStrTime(dtime):
    strhex = str(hex(dtime))[2:]
    if len(strhex) == 3:
        strhex = '[0' + strhex + ']'
    elif len(strhex) == 2:
        strhex = '[00' + strhex + ']'
    return strhex


def setTouch(dtime):
    global client
    if client:
        tmptime = dtime/1000.0 - delayNetTime
        if tmptime < 0:
            return False
        # client.send('0')
        strhex = intToHexStrTime(dtime)
        print(strhex)
        client.send(strhex)
        time.sleep(0.1)
        client.send('1')
        

def isControl():
    f = open('control.txt','r')
    s = f.read()
    f.close()
    if s == '0':
        return False
    else:
        return True

yolonet = None
    
yoloQueue_r = Queue(3) #yolo目标识别模块接收列队
netQueue_r = Queue(3)  #网络收发模块接收列队
tkQueue_r = Queue(3)    #tk界面图片显示模块接收图片列队,这个在主线程

def showBox(box):
    for k,v in box.items():
        tmpv = {'p':[v['x'],v['y']],'size':[v['w'],v['h']],'t':v['t'],'s':v['s']}
        print(tmpv)
#图片识别线程
def yoloThread(t):
    global yolonet
    labelsPath = os.getcwd() + os.sep +'yolo-net' +os.sep + 'my.names'
    weightsPath = os.getcwd() + os.sep +'yolo-net'+ os.sep + "yolov3.weights"
    configPath = os.getcwd() + os.sep +'yolo-net' + os.sep + "yolov3.cfg"
    yolonet = gameyolo.YOLONet(weightsPath, configPath, labelsPath)
    squeue = Queue(3)
    while True:
        time.sleep(0.1)
        if not yoloQueue_r.empty():
            print('yoloImage code')
            objtmp = yoloQueue_r.get()
            bx,oimg = getObjects(yolonet, objtmp.data)
            showBox(bx)
            dtime = getTouchTimeDelay(bx)
            if not dtime:
                time.sleep(3)
                continue
            print('dtime:%d'%(dtime))
            yobj = tktool.DataObj('box', dtime)
            netQueue_r.put(yobj)
            piloimg = Image.fromarray(cv2.cvtColor(oimg,cv2.COLOR_BGR2RGB))
            tkobj = tktool.DataObj('img', piloimg)
            tkQueue_r.put(tkobj)

isRcvClient = True

rcvTime = 0

def rcvServerData(dat):
    global isRcvClient
    global rcvTime
    rcvTime = time.time()
    isRcvClient = True
    print('rcvdata:%s'%(dat))

#网络收发线程
def netThread(t):
    global client
    global isRcvClient
    client = touchSocket.ClientSocket('192.168.0.193',isRecvBack = True)
    time.sleep(1)
    client.send('!')
    while True:
        time.sleep(0.1)
        if not netQueue_r.empty():
            objtmp = netQueue_r.get()
            dtime = objtmp.data
            if client and dtime:
                if dtime < 50:
                    return False
                # client.send('0')
                strhex = intToHexStrTime(dtime)
                print(strhex)
                client.send(strhex,rcvServerData)
                time.sleep(0.1)
                isRcvClient = False
                client.send('1',rcvServerData)


#获取一张新截图,并发送给YOLO识别线程
def callbackFunc(tapp):
    global isRcvClient
    global rcvTime
    print('callbackfunc')
    if isRcvClient:
        timep = time.time()
        if timep - rcvTime >=3:#防止接收回来时间太快,方块还没有停下的情况
            print('capimg')
            pilimg,cv2img = capImg()
            item = tktool.DataObj('img', cv2img)
            yoloQueue_r.put(item)


def main():
    netTh = threading.Thread(target=netThread,args=(None,))
    netTh.setDaemon(True)
    netTh.start()
    yoloTh = threading.Thread(target=yoloThread,args=(None,))
    yoloTh.setDaemon(True)
    yoloTh.start()

    root = tk.Tk()
    app = tktool.App(root,callbackFunc,tkQueue_r)
    root.geometry("+600+0")
    app.after(3000,app.onFrame)
    root.mainloop()
    
    

if __name__ == '__main__':
    main()

