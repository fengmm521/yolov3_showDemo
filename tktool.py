#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-08-01 11:28:48
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os,sys
import tkinter as tk
from PIL import Image, ImageTk
from queue import Queue

class DataObj():
    def __init__(self,pcmd,pdata):
        self.cmd = pcmd
        self.data = pdata

Dtime = 50

class App(tk.Frame):
    def __init__(self, master,backFunc,rQueue):
        super().__init__(master, width=400, height=300)
        self.pack()
        self.pilImage = Image.open("images/IMG_1614.jpg")
        w,h = self.pilImage.size
        w = int(w*0.3)
        h = int(h*0.3)
        self.pilImage = self.pilImage.resize((w,h),Image.ANTIALIAS)
        self.tkImage = ImageTk.PhotoImage(image=self.pilImage)
        self.label = tk.Label(self, image=self.tkImage)
        self.label.pack()
        self.imageIndex = 0
        self.rFunc = backFunc
        self.step = 0
        self.delayStep = Dtime
        self.imgQueue = rQueue
    def resizeImg(self,pilimg):
        w,h = pilimg.size
        w = int(w*0.3)
        h = int(h*0.3)
        rimg = pilimg.resize((w,h),Image.ANTIALIAS)
        return rimg

    def showImg(self,pilimg):
        img = self.resizeImg(pilimg)
        self.tkImage = ImageTk.PhotoImage(image=img)
        self.label.configure(image=self.tkImage)
        self.label.image = self.tkImage
        self.label.update()

    def processEvent(self):
        if not self.imgQueue.empty():
            objtmp = self.imgQueue.get()
            # piloimg = Image.fromarray(cv2.cvtColor(objtmp.data,cv2.COLOR_BGR2RGB))
            self.showImg(objtmp.data)
            self.step += 1
            print('step:%d'%(self.step))

    def onFrame(self):
        self.delayStep -=1
        if self.delayStep < 0:
            if self.rFunc:
                self.rFunc(self) #在主线程获取新截图
            self.delayStep = Dtime
        self.processEvent()
        self.after(100,self.onFrame)
        
def callbackFunc():
    pass

def main():
    #encoding=utf-8
    root = tk.Tk()
    app = App(root,callbackFunc)
    root.geometry("+600+0")
    app.after(3000,app.onFrame)

    root.mainloop()

#测试
if __name__ == '__main__':
    main()
    # test1()