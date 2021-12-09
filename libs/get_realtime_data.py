#import commons
#import get_historical_data
import math


#根据特定时间点的美元指数成分货币对报价，计算该时间点的美元指数报价
def calculate_dxy(symbols_rate_list):
    #初始化dxy_rate_list，列表元素第一个为symbol名称、第二个为时间戳、第三个为开盘价、第四个为最高价、第五个为最低价、第六个为收盘价
    dxy_rate_list = ['DXY',0,50.14348112,50.14348112,50.14348112,50.14348112]
    #创建各个货币对对应的比例
    dxy_portions = {
            'EURUSD':-0.576,
            'USDJPY':0.136,
            'GBPUSD':-0.119,
            'USDCAD':0.091,
            'USDSEK':0.042,
            'USDCHF':0.036
            }
    #遍历所有货币对报价，计算没有
    for symbol_rate in symbols_rate_list:
        #初始化dxy_rate_list，列表元素第一个为symbol名称、第二个为时间戳、第三个为开盘价、第四个为最高价、第五个为最低价、第六个为收盘价
        symbol_name = symbol_rate[0][0]
        symbol_ts = symbol_rate[0][1]
        symbol_open_price = symbol_rate[0][2]
        symbol_high_price = symbol_rate[0][3]
        symbol_low_price = symbol_rate[0][4]
        symbol_closed_price = symbol_rate[0][5]
        #将对应的货币对取对应的指数值，并与dxy_rate_list中开盘、最高、最低和收盘价相乘后直接修改其对应的值
        #时间戳赋值
        dxy_rate_list[1] = symbol_ts
        #开盘价计算及赋值
        dxy_rate_list[2] = math.pow(symbol_open_price,dxy_portions[symbol_name]) * dxy_rate_list[2]
        #最高价计算及赋值
        #EURUSD和GBPUSD为反向取值，所以取dxy的最高值的时候需要取这两个货币对的最低值，其余正相关货币对取最高值
        if symbol_name == 'EURUSD' or symbol_name == 'GBPUSD':
            dxy_rate_list[3] = math.pow(symbol_low_price,dxy_portions[symbol_name]) * dxy_rate_list[3]
        else:
            dxy_rate_list[3] = math.pow(symbol_high_price,dxy_portions[symbol_name]) * dxy_rate_list[3]
        #最低价计算及赋值
        #EURUSD和GBPUSD为反向取值，所以取dxy的最低值的时候需要取这两个货币对的最高值
        if symbol_name == 'EURUSD' or symbol_name == 'GBPUSD':
            dxy_rate_list[4] = math.pow(symbol_high_price,dxy_portions[symbol_name]) * dxy_rate_list[4]
        else:
            dxy_rate_list[4] = math.pow(symbol_low_price,dxy_portions[symbol_name]) * dxy_rate_list[4]
        #收盘价计算及赋值
        dxy_rate_list[5] = math.pow(symbol_closed_price,dxy_portions[symbol_name]) * dxy_rate_list[5]

    #返回结果列表
    return dxy_rate_list
'''
#根据mt5数据，计算该时间区间内的DXY报价
def gen_dxy_from_mt5(start,end,interval,account,db,mt5):
    #定义组成DXY的6个货币对名称，由于拉取数据时所用的标准化名称与实际名称一致并且没有特殊字符，所以这里就不去symbol method表中查，直接赋值即可
    dxy_symbol_list = ()

    #根据interval选择对应的处理逻辑，一切以最小粒度分钟为基础进行组合。
    result_list = []
    #目前仅支持1m和1h，如果有需要就继续添加if分支即可
    if interval == '1m':
        symbols_rate_list = []
        for symbol in dxy_symbol_list:
            symbol_rates = get_historical_data.get_historical_data_from_mt5(

    if interval == '1h':

    #返回结果列表
    return result_list

'''
