# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:38:49 2019

@author: Daniel
"""

from http import cookiejar
import urllib
from datetime import datetime
import json
import pandas as pd
from Proxy import ProxyIp
import random
from threading import Thread
from functools import reduce

class TechData(object):
    def __init__(self,symbol,begin='20190719',period='day',type_='before',count=1000,indicator='kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'):
        '''
        调用实例
        df = TechData(symbol='AG',begin='20190719',period='day',type_='before',count=1000,indicator='').request(proxy=True,update=False)   
        symbol：股票代码，忽略代码的大小写，A股调用需要区分上证或深证，例如三只松鼠：SZ300783，安集科技：SH688019，港股调用，中烟香港：06055
        begin：最新数据日期
        period：需要数据类型 -- 时间框架，默认为日线
        type_：默认before，指的是从最新日期数据之前
        count：需要数据的数量
        indicator：爬取数据需要的一些补充指标，例如kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance
        proxy:是否使用代理
        update：是否更新代理
        '''
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
    
    def request(self,proxy=False,**kwargs):
        opener = self.opener()
        if proxy:
            ip_list = ProxyIp().get(num=1,update=kwargs['update'])
            proxy_ip = random.choice(ip_list)
            ProxyHandler = urllib.request.ProxyHandler(proxy_ip)
            opener.add_handler(ProxyHandler)
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
        df.rename({'timestamp':'time'},axis='columns',inplace=True)
        df = self.check_nan(df)
        
        return df
                
    def check_nan(self,df):
        '''
        这个函数主要时为了检查percent这一列数据的空缺，如果有空缺值就需要依据close列计算出来
        '''
        nan_index = [i for i,item in enumerate(df.percent) if str(item) == 'nan' ]
        if len(nan_index) != 0:
            for i in nan_index:
                df.loc[i,'percent'] = ((df.loc[i,'close'] - df.loc[i-1,'close']) / df.loc[i-1,'close']) * 100
        return df

class MultiTechData(object):
    def __init__(self,symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='20190719',period='day',type_='before',count=1000,indicator='kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance',update=False):
        '''
        调用实例
        df = MultiTechData(symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='20190719',period='day',type_='before',count=1000,indicator='',update=False).multi_request(proxy=True)
        symbols：股票代码，必须是列表形式，忽略代码的大小写，A股调用需要区分上证或深证，例如三只松鼠：SZ300783，安集科技：SH688019，港股调用，中烟香港：06055
        begin：最新数据日期
        period：需要数据类型 -- 时间框架，默认为日线
        type_：默认before，指的是从最新日期数据之前
        count：需要数据的数量
        indicator：爬取数据需要的一些补充指标，例如kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance
        proxy:是否使用代理
        update：是否更新代理
        '''
        self.update = update
        self.ip_list = self.get_proxy_ip()
        self.init_url = 'https://xueqiu.com/'
        self.opener = self.opener_build()
        self.symbols = [item.upper() for item in symbols]
        self.begin = str(int(datetime.timestamp(datetime.strptime(begin,'%Y%m%d')) * 1000))
        self.period = period
        self.type_ = type_
        self.count = str(-count)
        self.indicator = indicator
        
        
        
    
    def opener_build(self):
        cj = cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(handler)
        opener.addheaders = [('user-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0')]
        opener.open(self.init_url)
        
        return opener
    
    def get_proxy_ip(self):
        return ProxyIp().get(num=10,update=self.update)
    
    def url_build(self,symbol):
        api = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?'
        data = {'symbol': symbol,
                'begin': self.begin,
                'period': self.period,
                'type': self.type_,
                'count': self.count,
                'indicator': self.indicator}
        data = urllib.parse.urlencode(data)
        url = api + data
        
        return url
        
    def multi_request(self,proxy=False):
        ip_list = self.ip_list
        threads,ls = [[] for _ in range(2)]
        for symbol in self.symbols:
            proxy_ip = random.choice(ip_list)
            thread = Thread(target=self.request,args=(proxy,symbol,ls,proxy_ip))      
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        df = reduce(lambda df_0,df_1: pd.concat([df_0,df_1],ignore_index=True),ls)
        
        return df
    
    def request(self,proxy,symbol,ls,proxy_ip):
        opener = self.opener
        if proxy:
            handler = urllib.request.ProxyHandler(proxy_ip)
            opener.add_handler(handler)
        webdata = json.loads(opener.open(self.url_build(symbol)).read().decode('utf-8'))['data']
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
        df.rename({'timestamp':'time'},axis='columns',inplace=True)
        df = self.check_nan(df)
        df['symbol'] = symbol
        ls.append(df)
        
    
    def check_nan(self,df):
        '''
        这个函数主要时为了检查percent这一列数据的空缺，如果有空缺值就需要依据close列计算出来
        '''
        nan_index = [i for i,item in enumerate(df.percent) if str(item) == 'nan' ]
        if len(nan_index) != 0:
            for i in nan_index:
                df.loc[i,'percent'] = ((df.loc[i,'close'] - df.loc[i-1,'close']) / df.loc[i-1,'close']) * 100
        return df

class IndexData(object):
    def __init__(self,begin='20190719',period='day',type_='before',count=1000,indicator='kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance',update=False):
        '''
        调用实例
        df = IndexData(begin='20210719',period='day',type_='before',count=1000,indicator='',update=False).request(index='csi300',proxy=True)
        参数说明见 MultiTechData
        '''
        self.csi_300_url = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000300cons.xls'
        self.csi_500_url = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000905cons.xls'
        self.sh_50_url   = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000016cons.xls'
        self.begin= begin
        self.period= period
        self.type_= type_
        self.count= count
        self.indicator= indicator
        self.update= update
    
    def index_request(self,index='csi300',proxy=True):
        # 从中正网站上获取最新的CSI300成分股
        index = index.lower()
        if index == 'csi300':
            df = pd.read_excel(self.csi_300_url)
        elif index == 'csi500':
            df = pd.read_excel(self.csi_500_url)
        elif index == 'sh50':
            df = pd.read_excel(self.sh_50_url)
        code = df['成分券代码Constituent Code'].apply(lambda x: str(x).rjust(6,'0'))
        exchange = df['交易所Exchange'].apply(lambda x: x[0]+x[-1])
        symbols = list(exchange + code) 
        df = MultiTechData(symbols=symbols,begin=self.begin,period=self.period,type_=self.type_,count=self.count,indicator=self.indicator,update=self.update).multi_request(proxy=True)
        
        return df
