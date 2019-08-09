# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 17:37:11 2019

@author: Daniel
"""

from data import TechData,MultiTechData,Params,IndexData,FundamentalData,MultiFundamentalData,IndexFundamentalData

if __name__ == '__main__':
    # 先更新一个IP代理 ---> 如果需要更新代理，请先将下一行注释去掉
    Params(update=True,num=10).flush_proxy()
    print('代理IP更新完成....')
    # 单线程数据调用
    df_single = TechData(symbol='SH603867',begin='19900415',end='20190806',period='day',type_='before',indicator='kline').request(proxy=True)
    df_multi = MultiTechData(symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='19900415',end='20190806',period='day',type_='before').multi_request(proxy=True)
    # 调用指数数据，本次演示调用所有A股数据
    df = IndexData(begin='19920101',end='20190819',period='day',type_='before').request(index='all',proxy=True,n=50)
    #df.to_csv('alldata.csv',index=False)
    # 单线程基本财务数据调用
    df = FundamentalData(symbol='SZ002027',type_='all',year=2018,count=1000).request(proxy=True)
    # 多线程基本财务数据调用
    lst = MultiFundamentalData(symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],type_='all',year=2018,count=1000,name_dict_update=False).multi_request(proxy=True)
    # 调用指数基本面数据，本次演示调用所有A股数据
    lst = IndexFundamentalData(type_='all',year=2019,count=1000,name_dict_update=False).request(index='sh50',proxy=True,n=50)


