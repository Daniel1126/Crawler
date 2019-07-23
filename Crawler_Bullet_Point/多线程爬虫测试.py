# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 12:06:34 2019

@author: Daniel
@conetent：本次测试会用股票数据进行
"""
import threading
import urllib
from http import cookiejar
import re
import json

def info():
    cj = cookiejar.CookieJar()
    handler = urllib.request.HTTPCookieProcessor(cj)    
    opener = urllib.request.build_opener(handler)
    opener.addheaders = [('User-Agent','Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)')]
    return opener


def get_code(codes):
    urls = []
    for code in codes:
        code = code.upper()
        dic = {'SZ':'2','SH':'1'}
        api = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id={}{}'.format(code[2:],dic[code[:2]])
        urls.append(api)
    return urls
    
def crawler(url):
    opener = info()
    pattern = re.compile('(\{.*?\})',re.S)
    try:
        webdata = opener.open(urllib.request.Request(url)).read().decode('utf-8')
        lock.acquire()
        data = json.loads(re.findall(pattern,webdata)[0])['Value']
        dic = {'name':data[2],'price':data[25],'percent':data[29]}
        print('股票名称: %s'%dic['name'],' 最新价格: %s'%dic['price'],'最新涨跌: %s%%'%dic['percent'])
        lock.release()
    except Exception as e:
        lock.acquire()
        print('抱歉,出现错误 --> %s'%e)
        lock.release()
if __name__ == '__main__':
    lock = threading.Lock()
    codes = ['sz000651','sh601318','sh600036','sz000895','sh601988','sz002597']
    urls = get_code(codes)
    threads = []
    for url in urls:
        thread = threading.Thread(target=crawler,args=(url,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
        
        