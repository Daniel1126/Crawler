# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 17:37:11 2019

@author: Daniel
"""

from data import TechData,MultiTechData,Params,IndexData
import time


if __name__ == '__main__':
    # 先更新一个IP代理 ---> 如果需要更新代理，请先将下一行注释去掉
    Params(update=True,num=10).flush_proxy()
    print('代理IP更新完成....')
    # 单线程数据调用
    #df_single = TechData(symbol='SH603867',begin='19900415',end='20190806',period='day',type_='before',indicator='kline').request(proxy=True)
    #df_multi = MultiTechData(symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='19900415',end='20190806',period='day',type_='before',indicator='kline').multi_request(proxy=True)
    #df = MultiTechData(symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='19920101',end='20190719',period='day',type_='before',indicator='kline').multi_request(proxy=True)
    df = IndexData(begin='19920101',end='20190819',period='day',type_='before').request(index='all',proxy=True,n=50)
    #df.to_csv('alldata.csv',index=False)
    #df.to_hdf('alldata.h5',key='df',mode='w')
