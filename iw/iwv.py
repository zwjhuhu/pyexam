# -*- coding: utf-8 -*-

import time
import re
import requests
import codecs
from bs4 import BeautifulSoup
import urllib

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

        info['likes']=likes
        info['views']=views
        info['thumburl']=thumburl
        info['vid']=vid
        info['vname']=vname
        info['userid']=userid
        info['username']=username
    except Exception as e:
            print (e)
    return info

def saveSqlFile(fileName,lst):
    try:
        f = codecs.open(fileName,'a','utf-8')
        for info in lst:
            vname = info['vname'].replace("'","\\'")
            userid = unicode(urllib.unquote(info['userid']),'utf-8').replace("'","\\'")
            username = info['username'].replace("'","\\'")

            tmp = u"insert into ivinfo (vid,vname,userid,username,thumburl,views,likes) values ('{}','{}','{}','{}','{}',{},{}) \
            on duplicate key update vname = '{}',userid='{}',username='{}',thumburl='{}',views={},likes={} ;\n".format( \
                info['vid'],vname,userid,username,info['thumburl'],info['views'],info['likes'],\
                vname,userid,username,info['thumburl'],info['views'],info['likes'])
            f.write(tmp)
    except Exception as e:
        print info
        print (e)
    finally:
        if 'f' in locals():
            f.close()

if __name__ == '__main__':

    #basepage = host + "/videos?f[0]=created%3A2018&sort=views"
    rootPath = "http://xxx"
    vlistPath = rootPath+'/videos'
    sqlFile = '/tmp/iv.sql'
    years = [2014,2015,2016,2017]
    lst = []
    for y in years:
        params = {'f[0]':'created:'+ str(y),'sort':'views'}
        referer,html = getHtmlTry(vlistPath,vlistPath,params,3)
        if html:
            page = getvTotalPage(html)
            #if page == 0:
            lst = getvInfos(html)
            if lst:
                saveSqlFile(sqlFile,lst)
            if page:
                for p in range(1,page+1):
                    params['page']=str(p)
                    time.sleep(1)
                    referer,html = getHtmlTry(vlistPath,referer,params,3)
                    lst = getvInfos(html)
                    if lst:
                        saveSqlFile(sqlFile,lst)

