# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:43:12 2019

@author: Daniel
"""

from data import TechData,MultiTechData


if __name__ == '__main__':
    '''
    调用实例
    '''
    # 单独调用数据
    df = TechData(symbol='00700',begin='20200801',period='day',type_='before',count=1000,indicator='').request(proxy=True,update=False) 
    # 多线程调用数据
    df = MultiTechData(symbols=['00700','SZ000651','AAPL','SZ002507','SH601318'],begin='20190719',period='day',type_='before',count=1000,indicator='',update=False).multi_request(proxy=True)
