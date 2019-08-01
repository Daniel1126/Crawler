# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:43:12 2019

@author: Daniel
"""

from data import TechData

if __name__ == '__main__':
    '''
    调用实例，如果proxy为False则不需要添加update参数，如果proxy为True则必须添加update参数
    '''
    df = TechData(symbol='00700',begin='20200801',period='day',type_='before',count=1000,indicator='').request(proxy=True,update=False) 
