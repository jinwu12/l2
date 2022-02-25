import ssl
from decimal import Decimal

import pandas as pd

from libs import commons, get_historical_data
from libs.database import *
import yfinance as yf

logger = commons.create_logger()


# 从yfinance拉取指定时间周期内的数据，并且将时间标准化为时间戳
def get_historical_data_from_yfinance(symbol, interval, start, end, timezone):
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # 根据symbol name获取拉取用的symbol value
    # 1m级别的数据只有近7天的
    # 根据输入参数拉取原始数据
    try:
        o_data = yf.download(tickers=symbol, interval=interval, start=start, end=end)
    except (ssl.SSLEOFError, ssl.SSLError):
        logger.error("%s:拉取%s~%s@interval:%s失败", symbol, str(start), str(end), interval)
        return False

    # 修改dataframe中的时间为时间戳并返回结果列表
    df = pd.DataFrame(o_data)
    result_list = []
    # 遍历dataframe中的每一行
    for pd_timestamp, row in df.iterrows():
        # 将第一列时间转timestamp
        ts = int(pd_timestamp.to_pydatetime().timestamp())
        # 获取开盘价、最高价、最低价和调整后的收盘价;价格取小数点后4位
        open_price = Decimal(row['Open']).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP")
        high_price = Decimal(row['High']).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP")
        low_price = Decimal(row['Low']).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP")
        close_price = Decimal(row['Adj Close']).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP")
        # 将该列列表附加到结果列表中进行嵌套
        result_list.append(dict(symbol=symbol, interval=interval, ts=ts,
                                price_open=open_price, price_high=high_price,
                                price_low=low_price, price_closed=close_price))
    return result_list


def fetch_data(start, end, interval):
    # 获取symbol列表
    symbols = Symbol.select()
    db = commons.db_connect()

    # 遍历symbol list，根据不同的method选择对应的处理函数，循环对symbol进行数据拉取和入库
    for symbol in symbols:
        yf_rates = []
        mt5_rates = []
        # 拉取yfinance数据源的symbol数据
        if symbol.method == 'get_historical_data_from_yfinance':
            data_list = get_historical_data_from_yfinance(symbol.symbol_value, interval, start, end, symbol.timezone)
            # 数据入库
            batch_save_by_symbol(symbol.name, data_list)
        if symbol.method == 'get_historical_data_from_mt5':
            # mt5数据间隔转换，需要把小时或分钟等间隔转换为TIMEFRAME；详情可参考：https://www.mql5.com/en/docs/integration/python_metatrader5/mt5copyratesfrom_py#timeframe
            # 目前只支持1h和1m转换，需要的话继续加条件就好了
            if interval == '1h':
                # mt5_rates = get_historical_data.get_historical_data_from_mt5(symbol_value, mt5.TIMEFRAME_H1, start, end,
                #                                                              mt5_account, db, mt5)
                print("fetch")
            if interval == '1m':
                print("fetch")
                # mt5_rates = get_historical_data.get_historical_data_from_mt5(symbol_value, mt5.TIMEFRAME_M1, start, end,
                #                                                              mt5_account, db, mt5)
            # 数据入库
            commons.insert_historical_original_data_to_db(symbol.name, mt5_rates, interval, db)
        # dxy历史数据入库
        if symbol.method == 'originate_from_mt5' and symbol.symbol_value == 'DXY_MT5':
            print(symbol.symbol_value)
            print("fetch")
            # dxy_rates = get_realtime_data.get_dxy_from_mt5(start, end, interval, mt5_account, db, mt5)
            # 数据入库
            # commons.insert_historical_original_data_to_db(symbol.name, dxy_rates, interval, db)
