# Crawler
自己常用的爬虫，主要爬取金融数据
调用方式和使用第三方库一样，必须保证该文档与你新创建的程序在同一个目录，或者在python能搜索到的目录
具体调用方式如下：
'''
from xueqiu_data_crawler import Crawler

if __name__ == '__main__':
    df = Crawler(symbol='AG',begin='20190719',period='day',type_='before',count=1000,indicator='').request()
    # 以下为注释部分
    # symbol:爬去股票的代码，例如阿里巴巴为BABA(忽略大小写)
    # begin：爬取数据的截至日期，例如20190719代表着最新数据为2019/07/19的数据
    # period：爬取数据的时间类型：day代表日线，类似的还有week，month，year等
    # type_：默认为before，不需要修改
    # count：代表要爬取的数据数量：1000代表爬去1000条数据，如果period为day，则1000个交易日的数据
    # indicator：代表抓取数据的金融指标，具体可以看代码，默认全部抓取

'''
