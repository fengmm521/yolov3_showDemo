#!/usr/bin/python
# -*- coding: utf-8 -*-
#创建SocketServerTCP服务器：

import socket
import sys

class ClientSocket(object):
    """docstring for ClientSocket"""
    def __init__(self, IP,Port = 23,isRecvBack = False):
        super(ClientSocket, self).__init__()
        self.serverIP = IP
        self.serverPort = Port
        self.isRecv = isRecvBack
        self.socket = None
        self.connectServer()
    def connectServer(self):
        self.socket = socket.socket()  # instantiate
        self.socket.connect((self.serverIP,self.serverPort))

    def send(self,data,rcvFunc = None):
        print('send:%s'%(data))
        self.socket.send(data.encode())
        if self.isRecv and len(data) == 1:
            data = self.socket.recv(1024).decode()  # receive response
            print('Received from server: ' + data)  # show in terminal
            # return data
            if rcvFunc:
                rcvFunc(data)
        else:
            print('do not receive server data')
            # return None

    def clsoe(self):
        self.socket.close()

def test():
    pass

if __name__ == '__main__':
    test()