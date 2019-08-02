# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:43:12 2019

@author: Daniel
"""

from data import TechData,MultiTechData,IndexData


if __name__ == '__main__':
    '''
    调用实例
    '''
    # 单独调用数据
    df_single = TechData(symbol='00700',begin='20200801',period='day',type_='before',count=1000,indicator='').request(proxy=True,update=False) 
    # 多线程调用数据
    df_multi = MultiTechData(symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='20190719',period='day',type_='before',count=1000,indicator='',update=False).multi_request(proxy=True)
    # 调用沪深300/上证50/中证500个股数据，由于同时获取多只股票数据，因此速度较慢
    df_CSI300 = IndexData(begin='20210719',period='day',type_='before',count=1000,indicator='',update=False).index_request(index='csi300',proxy=True)
    df_SH50   = IndexData(begin='20210719',period='day',type_='before',count=1000,indicator='',update=False).index_request(index='sh50',proxy=True)
    df_CSI500 = IndexData(begin='20210719',period='day',type_='before',count=1000,indicator='',update=False).index_request(index='csi500',proxy=True)
