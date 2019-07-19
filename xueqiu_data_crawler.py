# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 09:14:35 2019

@author: Daniel
"""
from http import cookiejar
import urllib
from datetime import datetime
import json
import pandas as pd
'''
1563586332636
'''

class Crawler(object):
    def __init__(self,symbol,begin='20190719',period='day',type_='before',count=1000,indicator='kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'):
        self.opener = self.opener_build
        self.symbol = symbol.upper()
        self.begin = str(int(datetime.timestamp(datetime.strptime(begin,'%Y%m%d')) * 1000))
        self.period = period
        self.type_ = type_
        self.count = str(-count)
        self.indicator = indicator
        self.init_url = 'https://xueqiu.com/'
    
    def opener_build(self):
        cj = cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(handler)
        opener.addheaders = [('user-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0')]
        opener.open(self.init_url)
        
        return opener
    
    def url_build(self):
        api = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?'
        data = {'symbol': self.symbol,
                'begin': self.begin,
                'period': self.period,
                'type': self.type_,
                'count': self.count,
                'indicator': self.indicator}
        data = urllib.parse.urlencode(data)
        url = api + data
        
        return url
    
    def request(self):
        opener = self.opener()
        webdata = json.loads(opener.open(self.url_build()).read().decode('utf-8'))['data']
        columns = webdata['column']
        item = webdata['item']
        item = [dict(zip(columns,i)) for i in item]
        dic = dict(zip(columns,[[] for i in range(len(columns))]))
        # 更新字典
        for dics in item:
            for k,v in dics.items():
                dic[k].append(v)
        df = pd.DataFrame(dic)
        df = df.sort_values('timestamp')
        df.timestamp = df.timestamp.apply(lambda x: datetime.fromtimestamp(x/1000).date())
        
        return df
                
        
if __name__ == '__main__':
    df = Crawler(symbol='AG',begin='20190719',period='day',type_='before',count=1000,indicator='').request()
    