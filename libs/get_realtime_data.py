import math
import time
from datetime import datetime, date, time, timezone
import pandas as pd
import sys
import pytz
sys.path.append('..')
from libs import get_historical_data
from libs import commons



#封装入库实时数据schedule函数              
def update_realtime_data(interval,db,mt5_account,mt5):                                             
    #初始化数据库连接
    db = commons.db_connect()
    method_list = get_historical_data.get_symbol_method(db)
    #获取symbol method对应的method list，并进行遍历
    for symbol_method in method_list:
        symbol_name = symbol_method[0]
        #根据symbol name获取拉取数据用的symbol value，用于获取数据
        symbol_value = commons.get_symbol_value(symbol_name,db)
        method = symbol_method[1]
        timezone = symbol_method[2]
        yf_rates = []
        mt5_rates = []
        dxy_rates = []
        #用于保存每种计算方式的字典
        data_dict = {'interval': interval}
        data_dict = {'symbol': symbol_name}
        data_dict = {'timezone': timezone}
        data_dict['method'] = method
        #结果列表
        result_list = []
        #拉取yfinance数据源的symbol数据
        if method == 'get_historical_data_from_yfinance':
            #生成时间间隔，必需按照时区转换时间后，按照隔日进行拉取
            yf_tz = pytz.timezone(timezone)
            yf_start_time = yf_tz.localize(date.today())
            yf_end_time = yf_start_time + timedelta(days=1)
            #将method附加到结果中
            #yfinance的分钟级及小时级数据拉取逻辑一致
            #拉取数据，并截取最后一个元素作为结果; 因为入库时executemany需要外侧是list+内层是tuple，所以此处需要用append而不能直接赋值
                yf_rates.append(get_historical_data.get_historical_data_from_yfinance(symbol_value,interval,yf_start_time,yf_end_time,timezone)[-1])
                #附加到data_dict中
                data_dict['value'] = yf_rates
                #数据入库
                commons.insert_historical_original_data_to_db(symbol_name,yf_rates,interval,db)
        #拉取mt5数据的symbol数据
        if method == 'get_historical_data_from_mt5':
            #获取当前的utc时间
            current_time = now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            #生成转换为UTC时区后的开始时间
            mt5_start_time = pd.to_datetime(current_time)
            #分钟级的逻辑
            if interval ='1m':
                #生成转换为UTC时区后的时间间隔
                mt5_start_time = pd.to_datetime(current_time)
                #对于XAUUSD等非外汇货币对，结束时间需要+1个interval
                #如果涉及有其他结束时间需要+1个interval的symbol，此处需要修改，可以考虑在db中新增interval_type进行配置
                if symbol_value == 'XAUUSD':
                    mt5_end_time = mt5_start_time + timedelta(minutes=1)
                else:
                    mt5_end_time = mt5_start_time
                #拉取数据
                mt5_rates = get_historical_data.get_historical_data_from_mt5(symbol_value,mt5.TIMEFRAME_M1,mt5_start_time,mt5_end_time,mt5_account,db,mt5)
                #附加到data_dict中
                data_dict['value'] = mt5_rates
            #小时级的逻辑
            if interval ='1h':
                #对于XAUUSD等非外汇货币对，结束时间需要+1个interval
                if symbol_value == 'XAUUSD':
                    mt5_end_time = mt5_start_time + timedelta(hours=1)
                else:
                    mt5_end_time = mt5_start_time
                #拉取数据
                mt5_rates = get_historical_data.get_historical_data_from_mt5(symbol_value,mt5.TIMEFRAME_H1,mt5_start_time,mt5_end_time,mt5_account,db,mt5)
                #附加到data_dict中
                data_dict['value'] = mt5_rates
            #数据入库
            commons.insert_historical_original_data_to_db(symbol_name,mt5_rates,interval,db)
        #从mt5拉取数据去生成的symbol数据,当前只有dxy，如果有需要就继续在此分支下添加if即可
        if method == 'originate_from_mt5':
            #获取当前的utc时间
            current_time = now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            #根据mt5等货币对报价，生成DXY
            if symbol_value == 'DXY-MT5':
                #生成转换为UTC时区后的开始时间
                mt5_start_time = current_time
                #由于DXY报价必然不会涉及贵金属报价，所以直接赋值为与开始时间相等即可
                mt5_end_time = mt5_start_time
                #拉取并计算dxy
                dxy_rates = get_dxy_from_mt5(mt5_start_time,mt5_end_time,interval,mt5_account,db,mt5)
                #附加到data_dict中
                data_dict['value'] = dxy_rates
                #数据入库
                commons.insert_historical_original_data_to_db(symbol_value,dxy_rates,interval,db)
        result_list.append(data_dict)
    return result_list




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
        symbol_name = symbol_rate[0]
        symbol_ts = symbol_rate[1]
        symbol_open_price = symbol_rate[2]
        symbol_high_price = symbol_rate[3]
        symbol_low_price = symbol_rate[4]
        symbol_closed_price = symbol_rate[5]
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

#根据mt5数据，计算该时间区间内的DXY报价
def get_dxy_from_mt5(start,end,interval,account,db,mt5):
    #start和end必须为utc时间(mt5默认就是使用的utc时间)
    #定义组成DXY的6个货币对名称，由于拉取数据时所用的标准化名称与实际名称一致并且没有特殊字符，所以这里就不去symbol method表中查，直接赋值即可
    dxy_symbol_list = ('EURUSD','USDJPY','GBPUSD','USDCAD','USDSEK','USDCHF')
    #根据interval选择对应的处理逻辑，一切以最小粒度分钟为基础进行组合。
    result_list = []
    symbols_rate_list = []
    skip =False
    dxy_result_list =[]
    #目前仅支持1m和1h，如果有需要就继续添加if分支即可
    #interval大于1分钟的最低价和最高价均不准确，详情请参考：https://trello.com/c/Eqf2N3m5
    if interval == '1m':
        #将起始时间秒强制取0,向下取整
        start_rounding_time = str(pd.to_datetime(start).replace(second=0,microsecond=0))
        end_rounding_time = str(pd.to_datetime(end).replace(second=0,microsecond=0))
        #获取起始时间的分钟差值
        delta_minute = int((time.mktime(time.strptime(end_rounding_time,"%Y-%m-%d %H:%M:%S"))-time.mktime(time.strptime(start_rounding_time,"%Y-%m-%d %H:%M:%S")))/60)
        if delta_minute < 0:
            print("结束时间:"+end+"大于等于开始时间:"+start+"!请检查输入参数!")
            exit()
        else:
            #初始化开始时间和结束时间
            start_time = datetime.strptime(start_rounding_time,"%Y-%m-%d %H:%M:%S")
            #拉取开始时间这个时间戳的数据，开始和结束时间一致即可
            end_time = start_time
            for minute in range(0,delta_minute):
                #遍历dxy_symbol_list,拉取这个时间周期的所有symbol报价,用于计算dxy
                for symbol in dxy_symbol_list:
                    symbol_rates = get_historical_data.get_historical_data_from_mt5(symbol,mt5.TIMEFRAME_M1,start_time,end_time,account,db,mt5)
                    #发现一个新问题，mt5中某个时间点的数据有可能为空。碰到这种情况就直接跳过即可
                    if symbol_rates != []:
                        symbols_rate_list.append(symbol_rates[0])
                    else:
                        #此处后续需要添加logging功能
                        print(symbol+"在"+str(start_time)+"的数据缺失!")
                        skip = True
                        break
                #每计算1分钟的dxy之后，需要将时间往前挪1分钟
                start_time = start_time+ timedelta(minutes=1)
                end_time = start_time
                result_list.append(tuple(calculate_dxy(symbols_rate_list)))
                #计算完毕后，清空这一个周期内的symbols_rate_list
                symbols_rate_list = []
    
    if interval == '1h':
        #将起始时间的分钟及秒强制取0,向下取整
        start_rounding_time = str(pd.to_datetime(start).replace(minute=0,second=0,microsecond=0))
        end_rounding_time = str(pd.to_datetime(end).replace(minute=0,second=0,microsecond=0))
        #获取起始时间的小时差值
        delta_hours = int((time.mktime(time.strptime(end_rounding_time,"%Y-%m-%d %H:%M:%S"))-time.mktime(time.strptime(start_rounding_time,"%Y-%m-%d %H:%M:%S")))/3600)
        if delta_hours <= 0:
            print("结束时间:"+end+"大于等于开始时间:"+start+"!请检查输入参数!")
            exit()
        else:
            #初始化开始时间和结束时间
            start_time = datetime.strptime(start_rounding_time,"%Y-%m-%d %H:%M:%S")
            #拉取开始时间这个时间戳的数据，开始和结束时间一致即可
            end_time = start_time
            for hour in range(0,delta_hours):
                #遍历dxy_symbol_list,拉取这个时间周期的所有symbol报价,用于计算dxy
                for symbol in dxy_symbol_list:
                    symbol_rates = get_historical_data.get_historical_data_from_mt5(symbol,mt5.TIMEFRAME_H1,start_time,end_time,account,db,mt5)
                    #发现一个新问题，mt5中某个时间点的数据有可能为空。碰到这种情况就直接跳过即可
                    if symbol_rates != []:
                        symbols_rate_list.append(symbol_rates[0])
                    else:
                        #此处后续需要添加logging功能
                        print(symbol+"在"+str(start_time)+"的数据缺失!")
                        skip = True
                        break
                #只要有一个货币对在这一小时的数据为空，则跳过这一小时的计算
                if skip == True:
                    break
                #每小时计算一次dxy,并附加到结果列表中;需要注意的是，此处的最高价和最低价均不准确。
                dxy_result_list = calculate_dxy(symbols_rate_list)
                #将内层转为tuple，方便后续使用mysql connector的excutemany入库
                result_list.append(tuple(dxy_result_list))
                #每计算1个小时的dxy之后，需要将时间往前挪1小时
                start_time = start_time+ timedelta(hours=1)
                end_time = start_time
                #计算完毕后，清空这一个周期内的symbols_rate_list
                symbols_rate_list = []
    return result_list

