import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime
from decimal import Decimal


#获取symbol对应拉取函数名称及对应时区
def get_symbol_method(db):
    #通过参数传入db连接
    symbol_method_db = db
    symbol_method_cursor = symbol_method_db.cursor()
    #获取全量symbol对应的method及时区
    get_all_symbol_method = 'select distinct symbol_name,method_name,timezone from Global_Config.Tbl_symbol_method'
    symbol_method_cursor.execute(get_all_symbol_method)
    #返回结果列表
    return symbol_method_cursor

#将时间文本转化为unix时间戳，以便存入db
def time_to_timestamp(time,timezone):
    tz = pytz.timezone(timezone)
    ts = tz.localize(time).timestamp()
    return int(ts)


#将时间戳转换为时间文本，以便展示或查看
def timestamp_to_time(timestamp,timezone):
    tz = pytz.timezone(timezone)
    time_str = datetime.fromtimestamp(timestamp,tz)
    return time_str

#标准化时间文本格式
def standardize_yfinance_time(time):
    #以-为分隔符，将时间文本进行拆分
    tmp = time.replace('-','|').replace('+','|').split("|")
    #只取前3个值，去掉最后的-5:00
    new_time=tmp[0]+'-'+tmp[1]+'-'+tmp[2]
    #返回时间
    return pd.to_datetime(new_time)


#组合standardize_yfinance_time、time_to_timestamp这两个函数，生成一个直接可以将yfinance返回的dataframe中的文本日期index直接转为时间戳的函数，用于通过map来rename dataframe中的index
def yf_date_to_timestamp(date,timezone):
    #格式化时间，去除脏字符串
    stime = standardize_yfinance_time(date)
    #根据时区，转换成时间戳
    stime_ts = time_to_timestamp(stime,timezone)
    #返回时间戳
    return stime_ts

#从yfinance拉取指定时间周期内的数据，并且将时间标准化为时间戳
def get_historical_data_from_yfinance(symbol,interval,start,end,timezone):
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # 根据输入参数拉取原始数据
    o_data = yf.download( tickers = symbol, interval = interval, start = start ,end = end)  
    #在源数据中增加一列symbol名称，方便入库使用
    o_data['ticker'] = symbol
    #修改dataframe中的时间为时间戳并返回结果列表
    df = pd.DataFrame(o_data)
    result_list = []
    #遍历dataframe中的每一行
    for index, row in df.iterrows():
        row_list = []
        #将第一列时间进行格式化处理，并根据对应时区转换为时间戳
        ts = time_to_timestamp(standardize_yfinance_time(str(index)),timezone)
        #获取开盘价、最高价、最低价和调整后的收盘价;价格取小数点后4位
        open_price = Decimal(row['Open']).quantize(Decimal("0.0001"), rounding = "ROUND_HALF_UP")
        high_price = Decimal(row['High']).quantize(Decimal("0.0001"), rounding = "ROUND_HALF_UP")
        low_price = Decimal(row['Low']).quantize(Decimal("0.0001"), rounding = "ROUND_HALF_UP")
        close_price = Decimal(row['Adj Close']).quantize(Decimal("0.0001"), rounding = "ROUND_HALF_UP")
        row_list.extend([ts,open_price,high_price,low_price,close_price])
        #将该列列表附加到结果列表中进行嵌套
        result_list.append(row_list)
    return result_list




