# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:43:12 2019

@author: Daniel
"""

from data import TechData

if __name__ == '__main__':
    '''
    调用实例
    '''
    df = TechData(symbol='BABA',begin='20190719',period='day',type_='before',count=1000,indicator='').request()   