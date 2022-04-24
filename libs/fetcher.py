import math
from datetime import datetime, timedelta
from decimal import Decimal

import MetaTrader5 as mt5
import pandas as pd
import pytz
import yfinance as yf
from retrying import retry

from libs.database import *
from libs.gen_combinations_price import *

logger = commons.create_logger()


# 从yfinance拉取指定时间周期内的数据，并且将时间标准化为时间戳
@retry(stop_max_attempt_number=3, wait_random_min=5, wait_random_max=10)
def get_historical_data_from_yfinance(symbol, interval, start, end, period=''):
    """
    从yfinance拉取指定时间区段(闭区间)、指定时间间隔的汇率(rates)数据
    :param symbol: 货币符号，使用Symbol对象时，请传value属性
    :param interval: 时间间隔，1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo，1m级别的数据只有近7天的
    :param start: 开始时间(datetime对象，构建时请指定为当前时区 => 到实现层时，将以当前时区(忽略datetime中的时区)转换为时间戳去获取具体的数据)
    :param end: 结束时间(datetime对象，构建时请指定为当前时区 = > 到实现层时，将以当前时区(忽略datetime中的时区)转换为时间戳去获取具体的数据)
    :param period: 拉取周期，默认为空，如果传了这个参数则不使用startt和end，避免拉取结果中多的最后一条奇怪数据，可选值有1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    :return: 汇率数据(dict列表)，如
        [{'symbol': '^TNX', 'interval': '1h', 'ts': 1641394800, 'price_open': '1.6490', 'price_high': '1.6580',
        'price_low': '1.6470', 'price_closed': '1.6530'}, ...]
    """
    try:
        if period:
            o_data = yf.download(tickers=symbol, interval=interval, period=period, progress=False)
        else:
            o_data = yf.download(tickers=symbol, interval=interval, start=start, end=end, progress=False)
    except:
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
        open_price = float(Decimal(row['Open']).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP"))
        high_price = float(Decimal(row['High']).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP"))
        low_price = float(Decimal(row['Low']).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP"))
        close_price = float(Decimal(row['Adj Close']).quantize(Decimal("0.0001"), rounding="ROUND_HALF_UP"))
        # 将该列列表附加到结果列表中进行嵌套
        result_list.append(dict(symbol=symbol, interval=interval, ts=ts,
                                price_open=open_price, price_high=high_price,
                                price_low=low_price, price_closed=close_price))
    return result_list


# 从mt5拉取制定时间周期内的数据，并将时间标准化为utc时间戳
def get_historical_data_from_mt5(symbol, timezone, interval, start, end):
    """
    从mt5拉取指定时间区段(闭区间)、指定时间间隔的汇率(rates)数据
    :param symbol: 货币符号，使用Symbol对象时，请传value属性
    :param timezone: Etc/GMT时区，对应Symbol的时区
    :param interval: 时间间隔，一般有一分钟(1m)，一小时(1h)，一天(1d)等，目前仅支持一分钟和一小时
    :param start: 开始时间(datetime对象，构建时请指定时区)
    :param end: 结束时间(datetime对象，构建时请指定时区)
    :return: 汇率数据(dict列表)，如
        [{'symbol': 'XAUUSD', 'interval': '1h', 'ts': 1648108800, 'price_open': 1940.27,
        'price_high': 1940.38, 'price_low': 1937.8, 'price_closed': 1938.18}, ...]
    """
    # 初始化mt5指定账号的mt5连接
    account_info = AccountInfo.get_by_id(1)
    auth = mt5.initialize(
        login=int(account_info.name),
        server=account_info.server,
        password=account_info.password
    )
    if not auth:
        logger.error("initialize() failed, error code: %s", mt5.last_error())
        return []

    # 使用copy_rates_range函数获取该区间内数据
    # ts数据要做偏移处理
    ts_off_set = commons.get_timezone_timestamp_offset(timezone)
    rates_range = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1 if interval == '1h' else mt5.TIMEFRAME_M1,
                                       start.timestamp() + ts_off_set, end.timestamp() + ts_off_set)
    if rates_range is None:
        logger.info("无数据")
        return []
    rates = rates_range.tolist()
    rates_list = []
    # 遍历结果列表
    for i in rates:
        # 将结果列表中的tuple元素仅截取时间戳、开盘价、最高价、最低价、收盘价，并拼接上symbol
        rates_list.append(dict(symbol=symbol, interval=interval, ts=i[0] - ts_off_set,  # 时间戳偏移处理
                               price_open=i[1], price_high=i[2],
                               price_low=i[3], price_closed=i[4]))
    # 获取完成，关闭连接
    mt5.shutdown()
    return rates_list


# 封装入库实时数据schedule函数
def update_realtime_data(interval, skip_symbol=[]):
    if interval not in ['1m', '1h']:
        raise Exception("Invalid interval:", interval)
    # 初始化数据库连接
    symbols = Symbol.select()
    # 结果列表
    result_list = []
    # 获取symbol method对应的method list，并进行遍历
    for symbol in symbols:
        symbol_name = symbol.name
        # 根据symbol name获取拉取数据用的symbol value，用于获取数据
        symbol_value = symbol.symbol_value
        method = symbol.method
        timezone = symbol.timezone
        rates = []
        # 如果遇到需要跳过的symbol，则直接跳过此symbol的拉取
        if symbol_name in skip_symbol:
            continue
        # 拉取yfinance数据源的symbol数据
        if method == 'get_historical_data_from_yfinance':
            # 实时数据拉取的start和end必须只传到日为止，比如2022-03-21，不能在后面带时分秒，否则会报错
            yf_start_time = datetime.now().date()
            yf_end_time = yf_start_time + timedelta(days=1)
            # yfinance的分钟级及小时级数据拉取逻辑一致
            # 拉取数据，并截取最后一个元素作为结果
            try:
                rates.append(get_historical_data_from_yfinance(
                    symbol_value, interval, yf_start_time, yf_end_time, '1d')[-1])
            except IndexError:
                logger.error("%s:数据拉取失败@%s", symbol_value, str(yf_start_time) + "~" + str(yf_end_time))
            else:
                # 数据入库
                batch_save_by_symbol(symbol_value, rates)

        # 拉取mt5数据的symbol数据
        elif method == 'get_historical_data_from_mt5':
            mt5_tz = pytz.timezone(timezone)
            # 开始时间为当前时间减去interval
            if interval == '1m':
                mt5_start_time = datetime.now(tz=mt5_tz).replace(second=0, microsecond=0) - timedelta(minutes=1)
            else:
                mt5_start_time = datetime.now(tz=mt5_tz).replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            # 结束时间等于开始时间
            mt5_end_time = mt5_start_time
            # 拉取数据
            try:
                rates.append(
                    get_historical_data_from_mt5(symbol_value, symbol.timezone, interval, mt5_start_time, mt5_end_time)[
                        0])
                # 数据入库
                batch_save_by_symbol(symbol_value, rates)
            except IndexError:
                logger.error("%s:数据拉取失败@%s", symbol_value, str(mt5_start_time) + "~" + str(mt5_end_time))

        # 从mt5拉取数据去生成的symbol数据,当前只有dxy，如果有需要就继续在此分支下添加if即可
        if method == 'originate_from_mt5':
            mt5_tz = pytz.timezone(timezone)
            # 开始时间为当前时间减去interval
            if interval == '1m':
                mt5_start_time = datetime.now(tz=mt5_tz).replace(second=0, microsecond=0) - timedelta(minutes=1)
            else:
                mt5_start_time = datetime.now(tz=mt5_tz).replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
                # 结束时间与开始时间相等
            mt5_end_time = mt5_start_time
            # 根据mt5等货币对报价，生成DXY
            try:
                rates.extend(get_dxy_from_mt5(mt5_start_time, mt5_end_time, interval))
                # 数据入库
                batch_save_by_symbol(symbol_value, rates)
            except IndexError:
                logger.error("%s:数据拉取失败@%s", symbol_value, str(mt5_start_time) + "~" + str(mt5_end_time))
        result_list.extend(rates)
    # print(datetime.now(), result_list)
    logger.info("%s", result_list)

    # 以<ts>_<interval>为key，分组
    data = {}
    for item in result_list:
        key = str(item['ts']) + '_' + item['interval']
        alist = data.get(key)
        if alist is None:
            alist = []
        alist.append(item)
        data[key] = alist

    # 计算组合价
    result = []
    for combination in Combination.select():
        for alist in data.values():
            item = calc_combo_price(alist, combination)
            if item:
                result.append(item)
    # 批量入库
    if len(result) > 0:
        CombinedSymbol.replace_many(result).execute()
    logger.info("入库组合价：%d， %s", len(result), result)

    return result_list


# 根据特定时间点的美元指数成分货币对报价，计算该时间点的美元指数报价
def calculate_dxy(symbols_rate_list):
    # 初始化dxy_rate_list，列表元素第一个为symbol名称、第二个为时间戳、第三个为开盘价、第四个为最高价、第五个为最低价、第六个为收盘价
    dxy_rate = dict(symbol='DXY_MT5', ts=0, price_open=50.14348112, price_high=50.14348112, price_low=50.14348112,
                    price_closed=50.14348112)
    # 创建各个货币对对应的比例
    dxy_portions = {
        'EURUSD': -0.576,
        'USDJPY': 0.136,
        'GBPUSD': -0.119,
        'USDCAD': 0.091,
        'USDSEK': 0.042,
        'USDCHF': 0.036
    }
    # 遍历所有货币对报价
    for symbol_rate in symbols_rate_list:
        # 初始化dxy_rate_list，列表元素第一个为symbol名称、第二个为时间戳、第三个为开盘价、第四个为最高价、第五个为最低价、第六个为收盘价
        symbol_name = symbol_rate['symbol']
        symbol_ts = symbol_rate['ts']
        symbol_open_price = symbol_rate['price_open']
        symbol_high_price = symbol_rate['price_high']
        symbol_low_price = symbol_rate['price_low']
        symbol_closed_price = symbol_rate['price_closed']
        # 将对应的货币对取对应的指数值，并与dxy_rate_list中开盘、最高、最低和收盘价相乘后直接修改其对应的值
        # 时间戳赋值
        dxy_rate['ts'] = symbol_ts
        # interval
        dxy_rate['interval'] = symbol_rate['interval']
        # 开盘价计算及赋值
        dxy_rate['price_open'] = math.pow(symbol_open_price, dxy_portions[symbol_name]) * dxy_rate['price_open']
        # 最高价计算及赋值
        # EURUSD和GBPUSD为反向取值，所以取dxy的最高值的时候需要取这两个货币对的最低值，其余正相关货币对取最高值
        if symbol_name == 'EURUSD' or symbol_name == 'GBPUSD':
            dxy_rate['price_high'] = math.pow(symbol_low_price, dxy_portions[symbol_name]) * dxy_rate['price_high']
        else:
            dxy_rate['price_high'] = math.pow(symbol_high_price, dxy_portions[symbol_name]) * dxy_rate['price_high']
        # 最低价计算及赋值
        # EURUSD和GBPUSD为反向取值，所以取dxy的最低值的时候需要取这两个货币对的最高值
        if symbol_name == 'EURUSD' or symbol_name == 'GBPUSD':
            dxy_rate['price_low'] = math.pow(symbol_high_price, dxy_portions[symbol_name]) * dxy_rate['price_low']
        else:
            dxy_rate['price_low'] = math.pow(symbol_low_price, dxy_portions[symbol_name]) * dxy_rate['price_low']
        # 收盘价计算及赋值
        dxy_rate['price_closed'] = math.pow(symbol_closed_price, dxy_portions[symbol_name]) * dxy_rate['price_closed']
    # 返回结果列表
    return dxy_rate


# 根据mt5数据，计算该时间区间内的DXY报价
def get_dxy_from_mt5(start, end, interval):
    # start和end必须为utc时间(mt5默认就是使用的utc时间)
    # 定义组成DXY的6个货币对名称，由于拉取数据时所用的标准化名称与实际名称一致并且没有特殊字符，所以这里就不去symbol method表中查，直接赋值即可
    dxy_symbol_list = {'EURUSD': 'Etc/GMT-3', 'USDJPY': 'Etc/GMT-3', 'GBPUSD': 'Etc/GMT-3', 'USDCAD': 'Etc/GMT-3',
                       'USDSEK': 'Etc/GMT-3', 'USDCHF': 'Etc/GMT-3'}
    # 根据interval选择对应的处理逻辑，一切以最小粒度分钟为基础进行组合。
    result_list = []

    # 目前仅支持1m和1h，如果有需要就继续添加if分支即可
    # interval大于1分钟的最低价和最高价均不准确，详情请参考：https://trello.com/c/Eqf2N3m5
    if interval == '1m':
        # 将起始时间秒强制取0,向下取整
        start_rounding_time = start.replace(second=0, microsecond=0)
        end_rounding_time = end.replace(second=0, microsecond=0)
        # 获取起始时间的分钟差值: end要比start大至少1分钟
        delta_minute = int((end_rounding_time.timestamp() - start_rounding_time.timestamp()) / 60)
        if delta_minute < 0:
            logger.error("结束时间(%s)要大于等于开始时间(%s)1分钟，请检查输入参数是否正确!", end, start)
            return []
        else:
            # 拉取开始时间这个时间戳的数据，开始和结束时间一致即可
            for minute in range(0, delta_minute + 1):
                # 清空这上一个周期内的symbols_rate_list
                symbols_rate_list = []
                # 重置skip值，避免只要有一个货币对在一个时间点出现问题就一直跳过
                skip = False
                # 遍历dxy_symbol_list,拉取这个时间周期的所有symbol报价,用于计算dxy
                the_time_by_minute = start_rounding_time + timedelta(minutes=minute)
                for symbol, timezone in dxy_symbol_list.items():
                    symbol_rates = get_historical_data_from_mt5(symbol, timezone, interval,
                                                                the_time_by_minute, the_time_by_minute)
                    # 发现一个新问题，mt5中某个时间点的数据有可能为空。碰到这种情况就直接跳过即可
                    if len(symbol_rates) > 0:
                        symbols_rate_list.append(symbol_rates[0])
                    else:
                        logger.error('%s在%s的数据缺失! @interval: %s', symbol, str(the_time_by_minute), interval)
                        skip = True
                        break

                # 只要有一个货币对在这一分钟的数据为空，则跳过这一分钟的计算
                if skip:
                    continue
                result_list.append(calculate_dxy(symbols_rate_list))

    elif interval == '1h':
        # 将起始时间的分钟及秒强制取0,向下取整
        start_rounding_time = start.replace(minute=0, second=0, microsecond=0)
        end_rounding_time = end.replace(minute=0, second=0, microsecond=0)
        # 获取起始时间的小时差值
        delta_hours = int((end_rounding_time.timestamp() - start_rounding_time.timestamp()) / 3600)
        if delta_hours < 0:
            logger.error("结束时间(%s)要大于等于开始时间(%s)1小时，请检查输入参数是否正确!", end, start)
            return []
        else:
            # 拉取开始时间这个时间戳的数据，开始和结束时间一致即可
            for hour in range(0, delta_hours + 1):
                # 清空这上一个周期内的symbols_rate_list
                symbols_rate_list = []
                # 重置skip值，避免只要有一个货币对在一个时间点出现问题就一直跳过
                skip = False
                # 遍历dxy_symbol_list,拉取这个时间周期的所有symbol报价,用于计算dxy
                the_time_by_hour = start_rounding_time + timedelta(hours=hour)
                for symbol, timezone in dxy_symbol_list.items():
                    symbol_rates = get_historical_data_from_mt5(symbol, timezone, interval,
                                                                the_time_by_hour, the_time_by_hour)
                    # 发现一个新问题，mt5中某个时间点的数据有可能为空。碰到这种情况就直接跳过即可
                    if len(symbol_rates) > 0:
                        symbols_rate_list.append(symbol_rates[0])
                    else:
                        logger.error('%s在%s的数据缺失! @interval: %s', symbol, str(the_time_by_hour), interval)
                        skip = True
                        break

                # 只要有一个货币对在这一小时的数据为空，则跳过这一小时的计算
                if skip:
                    continue
                # 每小时计算一次dxy,并附加到结果列表中;需要注意的是，此处的最高价和最低价均不准确。
                dxy_result_list = calculate_dxy(symbols_rate_list)
                # 将内层转为tuple，方便后续使用mysql connector的excutemany入库
                result_list.append(dxy_result_list)
    return result_list


def fetch_data(start, end, interval):
    # 获取symbol列表
    symbols = Symbol.select()

    # 遍历symbol list，根据不同的method选择对应的处理函数，循环对symbol进行数据拉取和入库
    for symbol in symbols:
        logger.info("开始抓取数据：%s between %s ~ %s @ %s" % (symbol.symbol_value, start, end, interval))
        # 拉取yfinance数据源的symbol数据
        if symbol.method == 'get_historical_data_from_yfinance':
            data_list = get_historical_data_from_yfinance(symbol.symbol_value, interval, start, end)
        elif symbol.method == 'get_historical_data_from_mt5':
            # mt5数据间隔转换，需要把小时或分钟等间隔转换为TIMEFRAME；详情可参考：https://www.mql5.com/en/docs/integration/python_metatrader5/mt5copyratesfrom_py#timeframe
            # 目前只支持1h和1m转换，需要的话继续加条件就好了
            data_list = get_historical_data_from_mt5(symbol.symbol_value, symbol.timezone, interval, start, end)
        elif symbol.method == 'originate_from_mt5' and symbol.symbol_value == 'DXY_MT5':
            data_list = get_dxy_from_mt5(start, end, interval)
        logger.info("数据抓取完成：%s[%s ~ %s]@%s => %d", symbol.name, start, end, interval, len(data_list))
        # 数据入库
        batch_save_by_symbol(symbol.symbol_value, data_list)
