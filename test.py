#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-08-01 11:28:48
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os,sys
import touchSocket
import time

def test1():
    # x = '06ff'
    # x = x[::-1]
    # print(x)
    a = 1000
    b= str(hex(a))
    print(b)

def test():
    # a= {'a':1,'b':2}
    # print(a.a)
    client = touchSocket.ClientSocket('192.168.0.193')
    time.sleep(1)
    client.send('!')
    x = '[06ff]'
    print(x)
    client.send(x)
    client.send('1')
    while True:
        client.send('1')
        time.sleep(10)

import tkinter as tk
from PIL import Image, ImageTk

class App(tk.Frame):
    def __init__(self, master=None):
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

    def resizeImg(self,pilimg):
        w,h = pilimg.size
        w = int(w*0.3)
        h = int(h*0.3)
        rimg = pilimg.resize((w,h),Image.ANTIALIAS)
        return rimg

    def processEvent(self):
        tmpimgpth = ''
        self.imageIndex += 1
        if self.imageIndex == 0:
            tmpimgpth = 'images/IMG_1614.jpg'
        elif self.imageIndex == 1:
            tmpimgpth = 'images/IMG_1615.jpg'
        else:
            tmpimgpth = 'images/IMG_1616.jpg'
            self.imageIndex = -1
        self.pilImage = Image.open(tmpimgpth)
        self.pilImage = self.resizeImg(self.pilImage)
        self.tkImage = ImageTk.PhotoImage(image=self.pilImage)
        self.label.configure(image=self.tkImage)
        self.label.image = self.tkImage
        self.label.update()
        print('xxx')
    def onFrame(self):
        self.processEvent()
        self.after(1000,self.onFrame)
        
def test2():
    #encoding=utf-8
    root = tk.Tk()
    app = App(root)
    root.geometry("+600+0")
    app.after(1000,app.onFrame)

    root.mainloop()
def test3():
    a= 'a/b/c.png'
    x = os.path.splitext(a)
    print(x)
#测试
if __name__ == '__main__':
    test3()
    # test1()