import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime
from decimal import Decimal
#import MetaTrader5 as mt5
from configparser import ConfigParser


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

#将指定时区的时间文本转化为utc时区的unix时间戳，以便存入db
def time_to_timestamp(time,timezone):
    tz = pytz.timezone(timezone)
    t_local = tz.localize(pd.to_datetime(time))
    t_utc = t_local.astimezone(pytz.UTC)
    ts = int(t_utc.timestamp())
    return ts


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
        #将第一列时间进行格式化处理，并根据对应时区转换为utc时间戳
        ts = time_to_timestamp(standardize_yfinance_time(str(index)),timezone)
        #获取开盘价、最高价、最低价和调整后的收盘价;价格取小数点后4位
        open_price = Decimal(row['Open']).quantize(Decimal("0.0001"), rounding = "ROUND_HALF_UP")
        high_price = Decimal(row['High']).quantize(Decimal("0.0001"), rounding = "ROUND_HALF_UP")
        low_price = Decimal(row['Low']).quantize(Decimal("0.0001"), rounding = "ROUND_HALF_UP")
        close_price = Decimal(row['Adj Close']).quantize(Decimal("0.0001"), rounding = "ROUND_HALF_UP")
        row_list.extend([symbol,ts,open_price,high_price,low_price,close_price])
        #将该列列表附加到结果列表中进行嵌套
        result_list.append(tuple(row_list))
    return result_list


#从db中读取mt5账号信息,走db读取参数死活无法连上mt5，走配置文件就可以……把这个函数改成从db里生成配置文件，再去读配置文件
def mt5_account_info(mt5_user_id,db):
    #根据账号名称，查询出账号详细信息
    mt5_account_db = db
    mt5_account_cursor = mt5_account_db.cursor()
    mt5_account_info_sql = 'select account_name,account_server,account_pass from Global_Config.account_info where account_platform =\'mt5\' and account_name=\''+mt5_user_id+'\''
    mt5_account_cursor.execute(mt5_account_info_sql)
    result = mt5_account_cursor.fetchall()
    #生成对应的配置文件
    config = ConfigParser()
    for i in range(len(result)):
        config_section_name = 'account_info_'+str(i)
        config[config_section_name] = {
                'account_name' : result[i][0],
                'account_server' : result[i][1],
                'account_pass' : result[i][2]
                }
    #写入配置文件
    cfg = open('account_config.ini',mode='w')
    config.write(cfg)

#从账号配置文件中读取指定账号的信息，初始化对应mt5连接
def init_mt5_from_ini(mt5_user_id,mt5):
        account_cfg = ConfigParser()
        account_cfg.read('account_config.ini')
        for i in account_cfg.sections():
            if account_cfg.get(i,"account_name") == mt5_user_id:
                if not mt5.initialize(
                        login=int(account_cfg.get(i,"account_name")),
                        server=account_cfg.get(i,"account_server"),
                        password=account_cfg.get(i,"account_pass")
                        ):
                        print("initialize() failed, error code =",mt5.last_error())
                        return False
                        quit()
                else:
                    return True
            else:
                print("account id:"+mt5_user_id+" is not found!")
                return False


#从mt5拉取制定时间周期内的数据，并将世界标准化为时间戳
def get_historical_data_from_mt5(symbol,interval,start,end,mt5_user,db,mt5):
    #将时间文本转为datetime对象
    start_t = pd.to_datetime(start)
    end_t = pd.to_datetime(end)

    #根据db生成账号信息配置文件
    mt5_account_info(mt5_user,db)

    #初始化mt5指定账号的mt5连接
    init_mt5_from_ini(mt5_user,mt5)

    #使用copy_rates_range函数获取该区间内数据
    #interval传入必须按照timeframe格式，如TIMEFRAME_M1、TIMEFRAME_H1。详情请参考:https://www.mql5.com/en/docs/integration/python_metatrader5/mt5copyratesfrom_py#timeframe
    #可以考虑将timeframe与interval对应关系入库
    #将结果转为list及结果中的tuple转换为list，方便后续使用
    #icmarkets+mt5默认返回的就是utc时间戳，无需额外转换
    rates = mt5.copy_rates_range(symbol,interval,start_t,end_t).tolist()
    rates_list = []
    #遍历结果列表
    for i in rates:
        #将结果列表中的tuple元素仅截取时间戳、开盘价、最高价、最低价、收盘价，并拼接上symbol
        j=()
        j=(symbol,)
        k=()
        k=j+i[0:5]
        #将转换过的tuple append到结果列表中
        rates_list.append(k)
    #获取完成，关闭连接
    mt5.shutdown()
    return rates_list

