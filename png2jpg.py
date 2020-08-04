#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-28 16:28:50
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os,sys

import json
# import timetool
import shutil
import random

from PIL import Image

if sys.version_info > (3,0):
    def cmp(a,b):
        import operator
        return operator.eq(a,b)


#获取脚本路径
def cur_file_dir():
    pathx = sys.argv[0]
    tmppath,_file = os.path.split(pathx)
    if cmp(tmppath,'') == 0:
        tmppath = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(tmppath):
        return tmppath
    elif os.path.isfile(tmppath):
        return os.path.dirname(tmppath)
    
#获取父目录
def GetParentPath(strPath):
    if not strPath:
        return None;
    lsPath = os.path.split(strPath);
    if lsPath[1]:
        return lsPath[0];
    lsPath = os.path.split(lsPath[0]);
    return lsPath[0];

#for python3
def cmp(a,b):
    return ((a>b)-(a<b))

#获取目录下的所有类型文件
def getAllExtFile(pth,fromatx = ".erl"):
    jsondir = pth
    jsonfilelist = []
    for root, _dirs, files in os.walk(jsondir):
        for filex in files:          
            #print filex
            name,text = os.path.splitext(filex)
            if cmp(text,fromatx) == 0:
                jsonArr = []
                rootdir = pth
                dirx = root[len(rootdir):]
                pathName = dirx +os.sep + filex
                jsonArr.append(pathName)
                (newPath,_name) = os.path.split(pathName)
                jsonArr.append(newPath)
                jsonArr.append(name)
                jsonfilelist.append(jsonArr)
            elif fromatx == ".*" :
                jsonArr = []
                rootdir = pth
                dirx = root[len(rootdir):]
                pathName = dirx +os.sep + filex
                jsonArr.append(pathName)
                (newPath,_name) = os.path.split(pathName)
                jsonArr.append(newPath)
                jsonArr.append(name)
                jsonfilelist.append(jsonArr)
    return jsonfilelist


#获取一个目录下的所有子目录路径
def getAllDirs(spth):
    files = getAllExtFile(spth,'.*')
    makedirstmp = []
    isOK = True
    # 分析所有要创建的目录
    for d in files:
        if d[1] != '/' and (not d[1] in makedirstmp): #创建未创建的目录层级
            tmpdir = d[1][1:]
            tmpleves = tmpdir.split('/')
            alldirs = getAllLevelDirs(tmpleves)
            for dtmp in alldirs:
                if not dtmp in makedirstmp:
                    makedirstmp.append(dtmp)
    return makedirstmp
#获取目录下的所有文件路径
def getAllFiles(spth,fromatx = '.*'):
    files = getAllExtFile(spth,fromatx)
    makedirstmp = []
    isOK = True
    # 分析所有要创建的目录
    for d in files:
        makedirstmp.append(d[0])
    return makedirstmp


def isFile(filename):
    try:
        with open(filename) as f:
            return True
    except IOError:
        return False

def finddir(arg,dirname,filenames):
    name,text = os.path.split(dirname)
    dirnametmp = str(dirname)
    if text and text[0] == '.':
        print(dirname)
        print(filenames)
        os.system('rm -r %s'%(dirname))
        return
    elif filenames:
        for f in filenames:
            if f[0] == '.' and isFile(dirname + f):
                fpthtmp = dirname + f
                if f.find(' '):
                    nf = f.replace(' ','\ ')
                    fpthtmp = dirname + nf
                print(dirname + f)
                os.system('rm  %s'%(fpthtmp))

#删除所有pth目录下的所有"."开头的文件名和目录名
def removeProjectAllHideDir(pth):
    alldirs = getAllDirs(pth)
    if not ('/' in alldirs):
        alldirs.append('/')
    for d in alldirs:
        tmpth = pth + d
        os.path.walk(tmpth, finddir, 0)


#获取一个路径中所包含的所有目录及子目录
def getAllLevelDirs(dirpths):
    dirleves = []
    dirtmp = ''
    for d in dirpths:
        dirtmp += '/' + d
        dirleves.append(dirtmp)
    return dirleves

#在outpth目录下创建ndir路径中的所有目录，是否使用决对路径
def makeDir(outpth,ndir):
    tmpdir = ''
    if ndir[0] == '/':
        tmpdir = outpth + ndir
    else:
        tmpdir = outpth + '/' + ndir
    print(tmpdir)
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)

# 创建一个目录下的所有子目录到另一个目录
def createDirs(spth,tpth):
    files = getAllExtFile(spth,'.*')
    makedirstmp = []
    isOK = True
    # 分析所有要创建的目录
    tmpfpth = fpth
    for d in files:
        if d[1] != '/' and (not d[1] in makedirstmp): #创建未创建的目录层级
            tmpdir = d[1][1:]
            tmpleves = tmpdir.split('/')
            alldirs = getAllLevelDirs(tmpleves)
            for dtmp in alldirs:
                if not dtmp in makedirstmp:
                    makeDir(tpth,dtmp)
                    makedirstmp.append(dtmp)

# 替换文件名
def replaceFileName(path,sname,replaceStr,tostr):
    a = sname
    tmpname = a.replace(replaceStr, tostr)
    outpath = path + tmpname
    oldpath = path + sname
    cmd = "mv %s %s"%(oldpath,outpath)
    print(cmd)
    os.system("mv %s %s"%(oldpath,outpath))

# 替换目录下的文件名中某个字符串为其他字符串
def renameDir(sdir,replacestr,tostr,exittype):
    files = getAllExtFile(sdir,fromatx = exittype)
    allfilepath = []
    for f in files:
        tmppath = sdir + f[1]
        filename = f[2] + exittype
        allfilepath.append([tmppath,filename])
    for p in allfilepath:
        replaceFileName(p[0], p[1], replacestr, tostr)


def getFileNameFromPath(fpth):
    tmp = fpth.split('/')[-1]
    fname = tmp.split('.')[0]
    return fname

filespath = 'sourceimage'
imagepath = 'images'
xmlpath = 'annotations'

trainNum = 0.8
valNum = 0.2

trainpth = 'train.txt'
valpth = 'val.txt'

def createDataFile():
    imgstmp = getAllFiles(filespath,'.png')
    xmlstmp = getAllFiles(filespath,'.xml')
    return imgstmp,xmlstmp

def copyfile(spth,tpth):
    f = open(spth,'rb')
    dat = f.read()
    f.close()
    f = open(tpth,'wb')
    f.write(dat)
    f.close()

def deleOldfile():
    if os.path.exists(imagepath):
        shutil.rmtree(imagepath)
    os.mkdir(imagepath)
    if os.path.exists(xmlpath):
        shutil.rmtree(xmlpath)
    os.mkdir(xmlpath)

def randomList(plist):
    dats = range(len(plist))
    dtmp = 0
    outnames = []
    while len(dats) > 0:
        dtmp = random.randint(0,len(dats)-1)
        print(dtmp,len(dats))
        outnames.append(dats[dtmp])
        dats.pop(dtmp)
        
    outlist = []

    for i,v in enumerate(outnames):
        outlist.append(plist[v])
    return outlist

def getFileNames(fs):
    outnames = []
    for i,v in enumerate(fs):
        tmp = getFileNameFromPath(v)
        outnames.append(tmp)
    return outnames

def createTrainAndValFile(names):
    tcount = int(len(names)*trainNum)
    vcount = len(names) - tcount
    trainstr = ''
    valstr = ''
    for i,v in enumerate(names):
        if i < tcount:
            trainstr += v + '\n'
        else:
            valstr += v + '\n'
    trainstr = trainstr[:-1]
    valstr = valstr[:-1]
    f = open('train.txt','w')
    f.write(trainstr)
    f.close()

    f = open('val.txt','w')
    f.write(valstr)
    f.close()

def conventPNG2JPEG(spth,tpth):
    im = Image.open(spth)
    rgb_im=im.convert('RGB')
    rgb_im.save(tpth)

def convertPngPTH2JpgPTH(spth):
    tmps = spth.split('.')
    jpegpth = ''
    if len(tmps) == 2:
        jpegpth = tmps[0]+'.jpg'
        return jpegpth
    return None

def main(pconf):
    pngspth = 'testimgpng'
    testpth = 'testimg'
    if os.path.exists(testpth):
        shutil.rmtree(testpth)
        os.mkdir(testpth)
    pngs = getAllFiles(pngspth,'.png')
    for i,v in enumerate(pngs):
        spth = pngspth + v
        jpgf = convertPngPTH2JpgPTH(v)
        if not jpgf:
            print('jpg file pth erro')
            print(spth)
            return
        tpth = testpth +jpgf
        conventPNG2JPEG(spth,tpth)
        print(spth,tpth)
    



def test():
    dats = range(100)
    dtmp = 0
    outnames = []
    while len(dats) > 0:
        dtmp = random.randint(0,len(dats)-1)
        print(dtmp,len(dats))
        outnames.append(dats[dtmp])
        dats.pop(dtmp)
        
    outimgs = []

    for i,v in enumerate(outnames):
    #     outimgs.append(imgs[v])
        print(v)
    print(len(outimgs))
    print(outnames)
    print(len(outnames))
    # print(len(outimgs))
#测试
if __name__ == '__main__':
    main(sys.argv)
    # test()
    
