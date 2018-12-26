# -*- coding: utf-8 -*-

import os
import json
import time
import urllib
import re
from bs4 import BeautifulSoup
import socks
import socket

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080)
socket.socket = socks.socksocket
import requests

g_userAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3322.4 Safari/537.36'

def getHtml(url,referer,payload):
    headers = {'User-Agent':g_userAgent,'referer':referer}
    res = requests.get(url,params=payload,headers=headers)
    print res.url
    html = ''
    if res.status_code == requests.codes.ok:
        res.encoding = 'utf-8'
        html = res.text
    return res.url,html


def getHtmlTry(url,referer,payload,trycount):
    count = 0
    u =''
    html = ''
    try:
        u,html = getHtml(url,referer,payload)
    except Exception as e:
        print (e)
        while count < trycount:
            try:
                u,html = getHtml(url,referer,payload)
            except Exception as e:
                print(e)
            finally:
                count+=1
                time.sleep(15)

    return u,html

#notice the site present page n use page=n-1
def getvTotalPage(html):
    page = 0
    if html:
        soup = BeautifulSoup(html,'lxml')
        plist = soup.select('ul.pager > li.pager-last > a')
        for p in plist:
            hr = p['href']
            pstr = re.match(r'.+page=(\d+).*',hr).group(1)
            if pstr:
                page = int(pstr)
    return page

def getvInfos(html):
    lst = []
    if html:
        soup = BeautifulSoup(html,'lxml')
        nlist = soup.select('div.node-video')
        for node in nlist:
            info = getvInfo(node)
            if info:
                lst.append(info)
    return lst

def getvInfo(node):
    likes = 0
    views = 0
    thumburl = 0
    vid = ''
    vname = ''
    userid = ''
    username = ''
    pri = 0
    info = {}
    try:
        n = node.select('div.icon-bg > .right-icon')[0]
        tmp = n.contents[-1].strip(' ').strip('\t').lower()
        if tmp.endswith('k'):
            likes = int(float(tmp[0:len(tmp)-1])*1000)
        else:
            likes = int(tmp)

        n = node.select('div.icon-bg > .left-icon')[0]
        tmp = n.contents[-1].strip(' ').strip('\t').lower()
        if tmp.endswith('k'):
            views = int(float(tmp[0:len(tmp)-1])*1000)
        else:
            views = int(tmp)

        n = node.select('div.field-item > a > img')[0]
        thumburl = n['src']
        vname = n.get('title',default='')

        n = node.select('h3.title > a')[0]
        tmp = n['href']
        vid = re.match(r'/videos/(.*)\??.*',tmp).group(1)
        if not vname:
            vname = n.string

        n = node.select('a.username')[0]
        tmp = n['href']
        userid = re.match(r'/users/(.*)\??.*',tmp).group(1)
        username = n.string.strip(' ')

        if node.select('.private-video'):
            pri = 1

        info['likes']=likes
        info['views']=views
        info['thumburl']=thumburl
        info['vid']=vid
        info['vname']=vname
        info['userid']=userid
        info['username']=username
        info['pri']=pri
    except Exception as e:
            print (e)
    return info

def mkdir(path):
    path = path.strip()
    isExists = os.path.exists(path)
    if not isExists:
        print 'create dir ',path
        os.makedirs(path)
    else:
        print 'dir ',path,' exist'

def dlFileQuiet(dlUrl,referer,vid,saveDir,suffix):
    headers = {'User-Agent':g_userAgent,'referer':referer}
    try:
        res = requests.get(dlUrl,headers=headers)
        if res.status_code == requests.codes.ok:
            with open(saveDir+'/'+vid+'.'+suffix, 'wb') as file:
                file.write(res.content)
        else:
            print 'download suffix for vid ',vid,'fail'
    except Exception as e:
        print(e)

def getDlUrl(url,referer,quality):
    headers = {'User-Agent':g_userAgent,'referer':referer}
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


def downloadImgAndV(basePath,referer,info,saveDir,quality):
    vid = info['vid']
    suffix = 'mp4'
    fileName = saveDir+'/'+vid+'.'+suffix;
    if os.path.isfile(fileName):
        print 'vid ',vid,' file ',fileName,' exist will skip'
        return

    thumburl = info['thumburl']
    apiUrl = basePath + '/api/video/'+vid
    print 'fecth vid ',vid,' info from ',apiUrl
    dlUrl = getDlUrl(apiUrl,referer,quality)
    if dlUrl:
        # thumburl
        '''if thumburl:
            if thumburl.startswith('//'):
                thumburl = 'http:' + thumburl
            else:
                thumburl = basePath + thumburl
            dlFileQuiet(thumburl,referer,vid,saveDir,'jpg')'''
        print 'get vdl url ',dlUrl
        dlFileQuiet(dlUrl,referer,vid,saveDir,suffix)


if __name__ == '__main__':

    basePath = 'http://xxx'
    #loadUsers()
    users = ['vnrg']

    saveDir = '/tmp/udl'
    lst = []
    quality = 1
    mkdir(saveDir)

    for u in users:
        vlistPath = basePath+'/users/'+u+'/videos'
        params = {}
        referer,html = getHtmlTry(vlistPath,vlistPath,params,3)
        if html:
            page = getvTotalPage(html)
            lst = getvInfos(html)
            for info in lst:
                downloadImgAndV(basePath,referer,info,saveDir,quality)
                time.sleep(5)
            if page:
                for p in range(1,page+1):
                    params['page']=str(p)
                    time.sleep(1)
                    referer,html = getHtmlTry(vlistPath,referer,params,3)
                    lst = getvInfos(html)
                    for info in lst:
                        downloadImgAndV(basePath,referer,info,saveDir,quality)
                        time.sleep(5)
