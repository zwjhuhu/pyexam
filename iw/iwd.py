# -*- coding: utf-8 -*-

import os
import json
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

def saveVFile(dlUrl,referer,vid,saveDir):
    ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3322.4 Safari/537.36'
    headers = {'User-Agent':ua,'referer':referer}
    res = requests.get(dlUrl,headers=headers)
    if res.status_code == requests.codes.ok:
        with open(saveDir+'/'+vid+'.mp4', 'wb') as file:
            file.write(res.content)
    else:
        print('download file for vid ',vid,'error')

def getDlUrl(url,referer,quality):
    ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3322.4 Safari/537.36'
    headers = {'User-Agent':ua,'referer':referer}
    res = requests.get(url,headers=headers)
    dlUrl = ''
    if res.status_code == requests.codes.ok:
        res.encoding = 'utf-8'
        paths = json.loads(res.text);
        if paths:
            if quality:
                dlUrl = paths[0]['uri']
            else:
                dlUrl = paths[-1]['uri']
    return dlUrl


def downloadV(basePath,vid,saveDir,quality):
    apiUrl = basePath + '/api/video/'+vid
    print('fecth vid ',vid,' info from ',apiUrl)
    referer = basePath+'/video/' + vid
    dlUrl = getDlUrl(apiUrl,referer,quality)
    print(dlUrl)
    #if dlUrl:
    #    print('get dl url ',dlUrl)
    #    saveVFile(dlUrl,referer,vid,saveDir)


def readVidsFile(filepath):
    vids = []
    with open(filepath) as file:
        lines = file.readlines(10000)
        for line in lines:
            vids.append(line.strip('\n'))

    return vids

if __name__ == '__main__':



    basePath = "http://xxx"

    vids = readVidsFile('d:/iw/vids.txt')
    saveDir = '/tmp/test'
    mkdir(saveDir)
    for vid in vids:
        try:
            downloadV(basePath,vid,saveDir,1)
            time.sleep(10)
        except Exception as e:
            print(e)
            print('download vid {} fail'.format(vid))
            time.sleep(20)