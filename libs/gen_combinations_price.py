import datetime
import traceback
from decimal import *

import pytz
from dateutil.relativedelta import relativedelta

from libs import commons

from collections import defaultdict

logger = commons.create_logger()


# 组合价格数据插入数据库
# https://trello.com/c/PV7xwqBM
def insert_combined_orignal_data(db, combined_price_list):
    # 根据combination_name-combination_id-combined_method-combination_3point_price-interval作为key并组成列表
    cursor = db.cursor()
    key_list = []
    key_data_dict = defaultdict(list)
    for combined_price in combined_price_list:
        combinaition_name = combined_price['combination_price'][0]
        combination_id = combined_price['combination_id']
        combined_method = combined_price['combined_method']
        combination_3point_price = combined_price['combination_3point_price']
        interval = combined_price['interval']
        db_year_and_month = datetime.datetime.fromtimestamp(int(combined_price['combination_price'][1])).strftime(
            '%Y%m')
        key = str(combination_id) + '_' + combined_method + '_' + str(
            combination_3point_price) + '_' + interval + '_' + db_year_and_month
        if key not in key_list:
            # 在存在新key的时候，将新key附到key_list中
            key_list.append(key)
            # 在存在新key的时候，生成对应的数据表
            create_tbl_sql = 'create table  IF NOT EXISTS production_combined_data.' + key + '_combined_symbol_original_data like production_combined_data.combined_symbol_original_data_template'
            cursor.execute(create_tbl_sql)
        # 按照key来拼接所有的组合价格，生成待批量插入db的list，需要包含key信息
        key_data_dict[key].append(tuple(combined_price['combination_price']))
    for key in key_list:
        # 生成模版sql
        sql_template = 'insert into production_combined_data.' + key + '_combined_symbol_original_data(symbol_name,ts,price_open,price_high,price_low,price_closed) values(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE price_open=VALUES(price_open), price_high=VALUES(price_high), price_low=VALUES(price_low), price_closed=VALUES(price_closed)'
        # 批量插入对应的表中
        cursor.executemany(sql_template, key_data_dict[key])
        db.commit()


# 拉取全量组合
# https://trello.com/c/LCDudDre
def get_symbol_combinations(db, symbol_methods):
    # 初始化db指针
    db_cursor = db.cursor()
    # 拼接拉取sql并拉取组合数据
    sql = 'select id,combination_name,symbol_list,combined_method,combination_3point_price,trading_symbol from Global_Config.symbol_combinations'
    db_cursor.execute(sql)
    sql_result = db_cursor.fetchall()
    result_list = []
    # 遍历结果
    for i in sql_result:
        id = int(i[0])
        combination_name = i[1]
        symbol_list = str(i[2])
        combined_method = i[3]
        tri_point_price = int(i[4])
        trading_symbol = i[5]
        # 判断combination_name是否为空，如果为空则根据symbol_list拉取symbol_name，与combined_method组成新的combination_name，然后update数据库中的combination_name
        if combination_name == '':
            for symbol_id in symbol_list.split(','):
                combination_name = combination_name + get_symbol_name_by_id(int(symbol_id), symbol_methods)[0][1] + '-'
            combination_name = combination_name + combined_method
            # 更新到db中
            sql = 'update Global_Config.symbol_combinations set combination_name="' + combination_name + '" where id=' + str(
                id)
            print(sql)
            db_cursor.execute(sql)
            db.commit()
        # 如果combination_3point_price为0，则运行calculate_combination_3point_price更新
        if tri_point_price == 0:
            tri_point_price = calculate_combination_3point_price(db, id)['tri_point_price']
        # 拼接结果
        result = {}
        result['id'] = id
        result['combination_name'] = combination_name
        result['symbol_list'] = symbol_list
        result['combined_method'] = combined_method
        result['tri_point_price'] = tri_point_price
        result['trading_symbol'] = trading_symbol
        result_list.append(result)
    return result_list


# 计算特定组合的3点价格
# 如果更新了symbol_list中的组合，需要将combination_3point_price设置为0，然后重新运行此函数
# https://trello.com/c/yREdUOrk
def calculate_combination_3point_price(db, combinations_id):
    # 初始化db指针
    db_cursor = db.cursor()
    # 拼接拉取combinations_id对应的symbol_list及3点价格的sql
    sql = 'select  id,symbol_list,combination_3point_price from Global_Config.symbol_combinations where id=' + str(
        combinations_id)
    # 拉取数据并赋值
    db_cursor.execute(sql)
    sql_result = db_cursor.fetchall()
    id = int(sql_result[0][0])
    symbol_list = sql_result[0][1]
    tri_point_price = sql_result[0][2]
    result = {}

    # 当combination_3point_price等于0时，证明该组合未曾生成过3点价格，则计算3点价格并更新到db中
    if tri_point_price == 0:
        tri_point_price = int(len(symbol_list.split(',')) * 3)
        sql = 'update Global_Config.symbol_combinations set combination_3point_price=' + str(
            tri_point_price) + ' where id=' + str(id)
        db_cursor.execute(sql)
        db.commit()
    # 当combination_3point_price不等于0时，证明该组合已产生过价格，直接返回即可
    result['id'] = id
    result['tri_point_price'] = tri_point_price
    return result


# 从Tbl_symbol_method表中拉取method_id对应的symbol name，供get_symbol_combinations中生成组合名称使用
def get_symbol_name_by_id(symbol_id, symbol_method_list):
    result = []
    for item in symbol_method_list:
        if item.get('method_id') == symbol_id:
            result.append((symbol_id, item.get('symbol_name')))
    return result


# 生成combination的历史数据
def get_historical_symbol_rates_list(db, start, end, interval):
    if start.find(" ") != -1:
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    else:
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    if end.find(" ") != -1:
        end_date = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    else:
        end_date = datetime.datetime.strptime(end, "%Y-%m-%d")
    # print(start_date, end_date)
    # 各symbol的数据，后续重组返回结果需要
    data = {}
    symbol_list = commons.get_all_symbol_attr(db)
    for symbol in symbol_list:
        # print(symbol)
        the_date = start_date
        # 循环
        while the_date.timestamp() <= end_date.timestamp():
            try:
                tbl = str.format("{}_{}_original_data_{}", symbol['symbol_name'], interval,
                                 datetime.datetime.utcfromtimestamp(the_date.timestamp()).strftime("%Y%m"))
                # print(tbl)
                sql = "select '%s', ts, price_open, price_high, price_low, price_closed from original_data_source.%s " \
                      "where ts between %d and %d order by ts" % (
                          symbol['symbol_value'], tbl, the_date.timestamp(), end_date.timestamp())
                # print(the_date, sql)
                cursor = db.cursor()
                cursor.execute(sql)
                result = cursor.fetchall()
                # print(result)
                exist = data.get(symbol['symbol_name'])
                if exist is None:
                    exist = result
                    data[symbol['symbol_name']] = exist
                exist = exist + result
            except:
                logger.error(traceback.format_exc())

            the_date = the_date + relativedelta(months=1)
            the_date = the_date.replace(day=end_date.day)

    # 组织返回结果
    # print(data)
    result = []
    the_date = start_date
    while the_date.timestamp() <= end_date.timestamp():
        data_in_same_ts = []
        ts = the_date.timestamp()
        for symbol in symbol_list:
            # print(symbol)
            data_list = data.get(symbol['symbol_name'])
            if data_list is not None and len(data_list) > 0 and data_list[0][1] == ts:
                # {'interval': '1m', 'symbol': 'XAUUSD', 'timezone': 'EET',
                # 'method': 'get_historical_data_from_mt5',
                # 'value': [('XAUUSD', 1640102220, 1796.79, 1797.32, 1796.69, 1797.15)]}
                value = data_list[0]
                item = {'interval': interval, 'symbol': symbol['symbol_name'], 'timezone': symbol['timezone'],
                        'method': symbol['method_name'], 'value': value}
                data_in_same_ts.append(item)
                del data_list[0]
        if len(data_in_same_ts) > 0:
            result.append(data_in_same_ts)
        if "1m" == interval:
            the_date = the_date + relativedelta(minutes=1)
        elif "1h" == interval:
            the_date = the_date + relativedelta(hours=1)
    # print(result)
    return result


# 使用strict_match方式来使用传入的symbol_rates_list和combination生成组合价格
def cal_comb_price_strict_match(symbol_rates_list, symbol_combination_id, db):
    db_cursor = db.cursor()
    sql = "select combination_name, symbol_list from Global_Config.symbol_combinations where id = %d" % symbol_combination_id
    db_cursor.execute(sql)
    sql_result = db_cursor.fetchone()
    combination_name = sql_result[0]
    # print(sql_result[1][0])
    sql = "select symbol_name, `3point_price` from Global_Config.Tbl_symbol_method where method_id in (%s)" % \
          sql_result[1][0]
    db_cursor.execute(sql)
    sql_result = db_cursor.fetchall()
    # print(sql_result)
    _3_point_price_map = {}  # 3点价格
    for symbol, price in sql_result:
        # print(symbol, "->", price)
        if price is None:
            logger.error("缺少3点价格数据：symbol=%s", symbol)
            return False, None
        _3_point_price_map[symbol] = price
    open_price_map = {}
    high_price_map = {}
    low_price_map = {}
    closed_price_map = {}
    interval = 60 * 60  # 默认1小时
    # 检查对应组合中的symbol是否都有报价，并记录最小和最大的时间戳
    min_ts = -1  # 最小的时间戳
    max_ts = -1  # 最大的时间戳
    symbol_price_list = []
    for symbol in sql_result:
        # print("check=>", symbol[0])
        # 同symbol的，取最前的一条报价
        find = False
        for sub_list in symbol_rates_list:
            for item in sub_list:
                if item['symbol'] == symbol[0]:
                    # print(item)
                    find = True
                    # 计算 价格/3点价*3
                    open_price_map[symbol[0]] = Decimal.from_float(item['value'][2]) / _3_point_price_map[symbol[0]] * 3
                    high_price_map[symbol[0]] = Decimal.from_float(item['value'][3]) / _3_point_price_map[symbol[0]] * 3
                    low_price_map[symbol[0]] = Decimal.from_float(item['value'][4]) / _3_point_price_map[symbol[0]] * 3
                    closed_price_map[symbol[0]] = Decimal.from_float(item['value'][5]) / _3_point_price_map[symbol[0]] * 3
                    if item['interval'] == '1m':
                        interval = 60
                    ts = item['value'][1]
                    if min_ts == -1 or ts < min_ts:
                        min_ts = ts
                    if max_ts == -1 or ts > max_ts:
                        max_ts = ts
                    break
            if find:
                # print("----------")
                break
        if not find:
            logger.error("symbol报价缺失：%s", symbol[0])
            return False, None
    # 比较各symbol报价的时差
    diff = max_ts - min_ts
    if diff > interval:
        logger.error("多个symbol报价时差过大：%d > %d", diff, interval)
        return False, None
    # 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
    # symbol价格取price_closed，3点价格从Tbl_symbol_method取
    open_combo_price = 0
    high_combo_price = 0
    low_combo_price = 0
    closed_combo_price = 0
    for price in open_price_map.values():
        open_combo_price += price
    for price in high_price_map.values():
        high_combo_price += price
    for price in low_price_map.values():
        low_combo_price += price
    for price in closed_price_map.values():
        closed_combo_price += price
    data = {
        'combination_id': symbol_combination_id, 'combined_method': 'strict_match',
        'symbol_3point_price': _3_point_price_map,
        'combination_3point_price': calculate_combination_3point_price(db, symbol_combination_id),
        'interval': '1m' if interval == 60 else '1h',
        'combination_price': [combination_name, max_ts, open_combo_price, high_combo_price,
                              low_combo_price, closed_combo_price]
    }
    return True, data
