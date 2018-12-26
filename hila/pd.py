# -*- coding: utf-8 -*-

import os
from bs4 import BeautifulSoup
import time
import socks
import socket

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080)
socket.socket = socks.socksocket

import requests

def mkdir(path):
    path = path.strip()
    isExists = os.path.exists(path)
    if not isExists:
        print('create dir ',path)
        os.makedirs(path)
    else:
        print('dir ',path,' exist')

def saveImgFile(dlUrl,referer,saveDir):
    ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3322.4 Safari/537.36'
    headers = {'User-Agent':ua,'referer':referer}
    print(dlUrl)
    pname = dlUrl[dlUrl.rindex('/')+1:]
    filepath = saveDir+'/'+ pname
    if os.path.exists(filepath):
        print('file exist ',filepath)
    else:
        res = requests.get(dlUrl,headers=headers)
        if res.status_code == requests.codes.ok:
            with open(filepath, 'wb') as file:
                file.write(res.content)
        else:
            print('download file from ',dlUrl,' error')

def getImgUrls(gid,url,referer):
    ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3322.4 Safari/537.36'
    headers = {'User-Agent':ua,'referer':referer}
    res = requests.get(url,headers=headers)
    imgUrls = []
    subdomain = 'aa'
    if gid%2 == 1:
        subdomain = 'ba'
    if res.status_code == requests.codes.ok:
        # res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text,'lxml')
        if soup:
            lst = soup.find_all('div',class_='img-url')
            for div in lst:
                url = div.string.strip()
                url = url[url.index('.'):]
                url = 'https://'+ subdomain+url
                imgUrls.append(url)
    return imgUrls


def downloadImgs(gid,basePath,saveDir):
    print('get all imgs from ',basePath)
    imgUrls = getImgUrls(gid,basePath,basePath)

    if imgUrls:
        for imgUrl in imgUrls:
            #print(imgUrl)
    #    print('get dl url ',dlUrl)
            saveImgFile(imgUrl,basePath,saveDir)


def readVidsFile(filepath):
    vids = []
    with open(filepath) as file:
        lines = file.readlines(10000)
        for line in lines:
            vids.append(line.strip('\n'))

    return vids

if __name__ == '__main__':



    basePath = 'https://xxx'
    gid = 1145942
    #vids = readVidsFile('d:/iw/vids.txt')
    cmname = 'xxx'
    saveDir = 'D:/hila/' + cmname

    mkdir(saveDir)
    downloadImgs(gid,basePath+str(gid)+'.html#1',saveDir)
