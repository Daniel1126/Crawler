# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 17:19:06 2019

@author: Daniel
"""

from http import cookiejar
import http
import glob
import urllib
from datetime import datetime
import json
import pandas as pd
from Proxy import ProxyIp
import random
import time
import os
from threading import Thread,Semaphore
from functools import reduce

class TechData(object):
    def __init__(self,symbol,begin='19920101',end='20201018',period='day',type_='before',indicator='kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'):
        '''
        调用实例
        df = TechData(symbol='SZ000651',begin='19920101',end='20190719',period='day',type_='before',indicator='kline').request(proxy=True)
        symbol：股票代码，忽略代码的大小写，A股调用需要区分上证或深证，例如三只松鼠：SZ300783，安集科技：SH688019，港股调用，中烟香港：06055
        begin：最新数据日期
        period：需要数据类型 -- 时间框架，默认为日线
        type_：默认before，指的是从最新日期数据之前
        count：需要数据的数量
        indicator：爬取数据需要的一些补充指标，例如kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance
        proxy:是否使用代理
        ---> 如果想更新代理，请提前调用  Params(update=True,num=1).flush_proxy()
        '''
        self.init_url = 'https://xueqiu.com/'
        self.opener = self.opener_build()
        self.symbol = symbol.upper()
        self.begin = str(int(datetime.timestamp(datetime.strptime(begin,'%Y%m%d')) * 1000))
        self.end = str(int(datetime.timestamp(datetime.strptime(end,'%Y%m%d')) * 1000))
        self.period = period
        self.type_ = type_
        self.indicator = indicator

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
                'end': self.end,
                'period': self.period,
                'type': self.type_,
                'indicator': self.indicator}
        data = urllib.parse.urlencode(data)
        url = api + data

        return url

    def request(self,proxy=False):
        opener = self.opener
        Judgement = True
        needle = 1
        while Judgement:
            if needle != 1: print('对 {symbol} 进行第{needle}次抓取......'.format(symbol=self.symbol,needle=needle))
            if proxy:
                ip_list = ProxyIp().get(num=1,update=False)
                proxy_ip = random.choice(ip_list)
                ProxyHandler = urllib.request.ProxyHandler(proxy_ip)
                opener.add_handler(ProxyHandler)
            try:
                data = opener.open(self.url_build(),timeout=10)
                if data.status == 200:
                    try:
                        webdata = data.read().decode('utf-8')
                    except http.client.IncompleteRead as e:   # 处理 chunked 读取错误，由于这里都是 json 所以就不再作 gzip 验证
                        webdata = e.partial.decode('utf-8')
                        if len(webdata) == 0:
                            webdata = '{}'
                    try:
                        webdata = json.loads(webdata)['data']
                        print('访问股票 --> %s'%(self.symbol))
                    except Exception as e:
                        print('Raise Error --> {e}'.format(e=e))
                    Judgement = False

            except KeyboardInterrupt:
                break
            except Exception as e:
                print('Raise Error --> %s'%e)
            needle += 1
        '''
        try:
            webdata = webdata.read().decode('utf-8')
        except http.client.IncompleteRead as e:   # 处理 chunked 读取错误，由于这里都是 json 所以就不再作 gzip 验证
            webdata = e.partial.decode('utf-8')
            if len(webdata) == 0:
                webdata = '{}'
        try:
            webdata = json.loads(webdata)['data']
            print('访问股票 --> %s'%(self.symbol))
        except Exception as e:
            print('Raise Error --> {e}'.format(e=e))
        '''
        df = self.data_processing(webdata,proxy)

        return df

    def data_processing(self,webdata,proxy):
        try:
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
        except Exception as e:
            print('Raise Error --> %s'%e)
            time.sleep(5)
            df = self.request (proxy)

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
    def __init__(self,symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='20201018',end='19920101',period='day',type_='before',indicator='kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'):
        '''
        调用实例
        df = MultiTechData(symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='19920101',end='20190719',period='day',type_='before',indicator='kline').multi_request(proxy=True)
        '''
        self.symbols = symbols
        self.begin = begin
        self.end = end
        self.period = period
        self.type_ = type_
        self.indicator = indicator

    def requests(self,symbol,proxy,ls):
        df = TechData(symbol=symbol,begin=self.begin,end=self.end,period=self.period,type_=self.type_,indicator=self.indicator).request(proxy=proxy)
        df['symbol'] = symbol
        ls.append(df)

    def multi_request(self,proxy=False):
        threads,ls = [[] for _ in range(2)]
        for symbol in self.symbols:
            thread = Thread(target=self.requests,args=(symbol,proxy,ls))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        print('正在拼接数据，请稍等......')
        df = reduce(lambda df_0,df_1: pd.concat([df_0,df_1],ignore_index=True),ls)
        print('本次数据拼接完成..........')

        return df

class IndexData(object):
    def __init__(self,begin='19920101',end='20190719',period='day',type_='before',indicator='kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'):
        '''
        调用实例
        df = IndexData(begin='19920101',end='20190719',period='day',type_='before',indicator='kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance').request(index='csi300',proxy=True,n=50)
        参数说明见 MultiTechData
        n：只针对index='all'这种情况下才会使用，n越大对电脑配置和网络条件越高，目前n=50表现较为稳定，可以通过降低n来提升抓取数据的稳定性
        '''
        self.csi_300_url = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000300cons.xls'
        self.csi_500_url = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000905cons.xls'
        self.sh_50_url   = 'http://www.csindex.com.cn/uploads/file/autofile/cons/000016cons.xls'
        self.all_csi_url = 'http://www.csindex.com.cn/uploads/file/autofile/cons/930903cons.xls'
        self.begin= begin
        self.period= period
        self.type_= type_
        self.end= end
        self.indicator= indicator

    def request(self,index='csi300',proxy=True,n=50):
        # 从中正网站上获取最新的CSI300成分股
        index = index.lower()
        if index == 'csi300':
            df = pd.read_excel(self.csi_300_url)
        elif index == 'csi500':
            df = pd.read_excel(self.csi_500_url)
        elif index == 'sh50':
            df = pd.read_excel(self.sh_50_url)
        elif index == 'all':
            df = pd.read_excel(self.all_csi_url)

        code = df['成分券代码Constituent Code'].apply(lambda x: str(x).rjust(6,'0'))
        exchange = df['交易所Exchange'].apply(lambda x: x[0]+x[-1])
        symbols = list(exchange + code)
        if index == 'all':
            symbols_list = self.chunk(symbols,num=n)
            symbols_list = list(symbols_list)
            if 'tmp' in os.listdir():
                content = os.listdir('./tmp')
                if content:
                    for file in content:
                        os.remove('./tmp/'+file)
                        os.rmdir('tmp')
                else:
                    os.rmdir('tmp')
            os.mkdir('tmp')
            for i,code_ls in enumerate(symbols_list):
                df = MultiTechData(symbols=code_ls,begin=self.begin,end=self.end,period=self.period,type_=self.type_,indicator=self.indicator).multi_request(proxy=proxy,n=n)
                df.to_csv('./tmp/%s.csv'%i)
                print('正在抓取数据 ({i:>2}/{length})......'.format(i=i+1,length=len(symbols_list)))
                time.sleep(10)
            print('数据抓取完成，正在处理，请稍后.....')
            FileName = glob.glob('./tmp/*.csv')
            ls = [pd.read_csv(file) for file in FileName]
            for file in FileName:
                os.remove(file)
            os.rmdir('tmp')
            df = reduce(lambda df_0,df_1: pd.concat([df_0,df_1],ignore_index=True),ls)
        else:
            df = MultiTechData(symbols=symbols,begin=self.begin,end=self.end,period=self.period,type_=self.type_,indicator=self.indicator).multi_request(proxy=proxy,n=n)
        return df

    def chunk(self,symbols,num=50):
        for i in range(0,len(symbols),num):
            yield symbols[i:i+num]


class Params(object):
    def __init__(self,update=True,num=1):
        self.update = update
        self.num = num

    def flush_proxy(self):
        '''
        返回一个代理IP列表
        '''
        ProxyIp().get(num=self.num,update=self.update)
