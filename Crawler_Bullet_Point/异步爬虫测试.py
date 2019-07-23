# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 14:51:55 2019

@author: Administrator
"""

import aiohttp
import asyncio
import re
import json

def get_code(codes):
    urls = []
    for code in codes:
        code = code.upper()
        dic = {'SZ':'2','SH':'1'}
        api = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id={}{}'.format(code[2:],dic[code[:2]])
        urls.append(api)
    return urls

def data_processing(resp):
    pattern = re.compile('(\{.*?\})',re.S)
    data = json.loads(re.findall(pattern,resp)[0])['Value']
    dic = {'name':data[2],'price':data[25],'percent':data[29]}
    return dic


async def fetch(session,url):
    try:
        async with session.get(url) as response:
            resp = await response.text()
            dic = data_processing(resp)
            print('股票名称: %s'%dic['name'],' 最新价格: %s'%dic['price'],'最新涨跌: %s%%'%dic['percent'])
            await asyncio.sleep(3)
    except Exception as e:
        print('出现问题:%s'%e)
    

async def run(sema,url):
    async with sema:
        async with aiohttp.ClientSession() as session:
            await fetch(session,url)
        #await asyncio.sleep(2)



if __name__ == '__main__':
    codes = ['sz000651','sh601318','sh600036','sz000895','sh601988','sz002597']
    urls = get_code(codes)
    sema = asyncio.Semaphore(3)
    tasks = [asyncio.ensure_future(run(sema,url)) for url in urls]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    
    
    
    
    
    
    
    
    
    