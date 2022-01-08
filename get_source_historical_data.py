from libs import commons
from libs import get_historical_data
import sys
import MetaTrader5 as mt5
from libs  import get_realtime_data


#获取对应的参数
start = '2021-12-26'
end = '2022-01-01'
interval = '1m'
#mt5数据源专用账号
mt5_account = '5348288'

#获取symbol列表对应的method list
db = commons.db_connect()
method_list = get_historical_data.get_symbol_method(db)

#遍历method list，根据不同的method选择对应的处理函数，循环对symbol进行数据拉取和入库
for symbol_method in method_list:
    symbol_name = symbol_method[0]
    #根据symbol name获取对应拉取接口的symbol标准化名称
    symbol_value = commons.get_symbol_value(symbol_name,db)
    method = symbol_method[1]
    timezone = symbol_method[2]
    yf_rates = []
    mt5_rates = []
    mt5_interval = ''
    #拉取yfinance数据源的symbol数据
    if method == 'get_historical_data_from_yfinance':
        yf_rates = get_historical_data.get_historical_data_from_yfinance(symbol_value,interval,start,end,timezone)
        #数据入库
        commons.insert_historical_original_data_to_db(symbol_name,yf_rates,interval,db)
    if method == 'get_historical_data_from_mt5':
        #mt5数据间隔转换，需要把小时或分钟等间隔转换为TIMEFRAME；详情可参考：https://www.mql5.com/en/docs/integration/python_metatrader5/mt5copyratesfrom_py#timeframe
        #目前只支持1h和1m转换，需要的话继续加条件就好了
        if interval == '1h':
            mt5_rates = get_historical_data.get_historical_data_from_mt5(symbol_value,mt5.TIMEFRAME_H1,start,end,mt5_account,db,mt5)
        if interval == '1m':
            mt5_rates = get_historical_data.get_historical_data_from_mt5(symbol_value,mt5.TIMEFRAME_M1,start,end,mt5_account,db,mt5)
        #数据入库
        commons.insert_historical_original_data_to_db(symbol_name,mt5_rates,interval,db)
    #dxy历史数据入库
    if method == 'originate_from_mt5' and symbol_value == 'DXY_MT5':
        print(symbol_value)
        dxy_rates = get_realtime_data.get_dxy_from_mt5(start,end,interval,mt5_account,db,mt5)
        #数据入库
        commons.insert_historical_original_data_to_db(symbol_name,dxy_rates,interval,db)



