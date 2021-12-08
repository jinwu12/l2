import sys
import commons
import get_historical_data


#根据特定时间点的美元指数成分货币对报价，计算该时间点的美元指数报价
def calculate_dxy(symbols_rate_list):

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
