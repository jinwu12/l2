import datetime
import traceback
from collections import defaultdict, Counter
from decimal import *

from dateutil.relativedelta import relativedelta
from playhouse.shortcuts import model_to_dict

from libs.database import *

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


# 检查组合数据是否完备，完善名称和3点价格
# https://trello.com/c/LCDudDre
# 如果更新了symbol_list中的组合，需要将combination_3point_price设置为0，然后重新运行此函数
def check_combinations():
    combinations = Combination.select()
    for combination in combinations:
        # combination_name规则：取symbol_list中各symbol_name与combined_method组成新的combination_name
        if len(combination.name) < 1:
            combination_name = ''
            for id in combination.symbol_list.split(','):
                combination_name += Symbol.get_by_id(int(id)).name + '-'
            combination_name += combination.combined_method
            combination.update(name=combination_name).execute()
        # 重算一次3点价格
        combination.update(combination_3point_price=calculate_combination_3point_price(combination)).execute()


# 计算特定组合的3点价格
# https://trello.com/c/yREdUOrk
def calculate_combination_3point_price(combination):
    return int(len(combination.symbol_list.split(',')) * 3)


# 生成combination的历史数据（https://trello.com/c/ISevINO7）
def get_historical_symbol_rates_list(start, end, interval):
    # print(start, end)
    # 各symbol的数据，后续重组返回结果需要，<symbol名, >
    data = {}
    symbols = Symbol.select()
    for symbol in symbols:
        # print(symbol)
        try:
            tbl = get_model_table_by_symbol(symbol.symbol_value)
            # print(tbl)
            sql = "select '%s', ts, price_open, price_high, price_low, price_closed from original_data_source.%s " \
                  "where ts between %d and %d order by ts" % (
                      symbol.symbol_value, tbl, start.timestamp(), end.timestamp())
            # print(the_date, sql)
            cursor = data_source_db.execute_sql(sql)
            result = list(cursor.fetchall())
            # print(result)
            exist = data.get(symbol.name)
            if exist is None:
                exist = result
                data[symbol.name] = exist
            exist = exist + result
        except:
            logger.error(traceback.format_exc())

    # 组织返回结果
    # print(data)
    result = []
    the_date = start
    while the_date.timestamp() <= end.timestamp():
        data_in_same_ts = []
        ts = the_date.timestamp()
        for symbol in symbols:
            # print(symbol)
            data_list = data.get(symbol.name)
            if data_list is not None and len(data_list) > 0 and data_list[0][1] == ts:
                # {'interval': '1m', 'symbol': 'XAUUSD', 'timezone': 'EET',
                # 'method': 'get_historical_data_from_mt5',
                # 'value': [('XAUUSD', 1640102220, 1796.79, 1797.32, 1796.69, 1797.15)]}
                value = data_list[0]
                item = {'interval': interval, 'symbol': symbol.name, 'timezone': symbol.timezone,
                        'method': symbol.method, 'value': value}
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


def calc_combo_price(symbol_rates_list, combination, mode='strict_match'):
    valid_rates_list = []  # 最终用来计算的数据
    trio_point_price_map = {}  # 3点价格
    # 判断symbol_rates_list是否包含组合要求的所有symbol的数据
    for symbol_id in combination.symbol_list.split(','):
        symbol = global_cache.get_symbol_by_id(int(symbol_id))
        if symbol is None:
            logger.error("不存在对应id的symbol：id=%s", symbol_id)
            return False, None
        elif symbol.trio_point_price is None:
            logger.error("缺少3点价格数据：symbol=%s", symbol.name)
            return False, None
        symbol_value = symbol.symbol_value
        trio_point_price_map[symbol_value] = float(symbol.trio_point_price)
        found = False
        for rate in symbol_rates_list:
            if rate['symbol'] == symbol_value:
                valid_rates_list.append(rate)
                found = True
                break
        if not found:
            logger.error("计算组合价格时缺少对应symbol数据：combo_id=%d, symbol_list=%s, 缺少%s", combination.id,
                         combination.symbol_list, symbol_value)
            return False, None
    first_rate = valid_rates_list[0]
    first_ts = first_rate['ts']
    first_interval = first_rate['interval']
    max_gap = 60 if first_interval == '1m' else 60 * 60  # 1个interval的时间间隔
    min_ts = first_ts
    max_ts = first_ts
    for item in valid_rates_list[1:]:
        if item['interval'] != first_interval:
            logger.error("提供的数据interval不一致：%s", valid_rates_list)
            return False, None
        ts = item['ts']
        if first_ts != ts:
            min_ts = min_ts if min_ts <= ts else ts
            max_ts = max_ts if max_ts >= ts else ts
    # 判断所有时间戳是否一致
    gap = max_ts - min_ts
    if gap > max_gap:
        logger.error("提供的数据时差超过1个interval：%s", valid_rates_list)
        return False, None
    # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
    open_combo_price = 0
    high_combo_price = 0
    low_combo_price = 0
    closed_combo_price = 0
    ts_list = []
    for item in valid_rates_list:
        symbol_name = item['symbol']
        ts_list.append(item['ts'])
        # 计算 价格/3点价*3
        open_combo_price += item['price_open'] / trio_point_price_map[symbol_name] * 3
        high_combo_price += item['price_high'] / trio_point_price_map[symbol_name] * 3
        low_combo_price += item['price_low'] / trio_point_price_map[symbol_name] * 3
        closed_combo_price += item['price_closed'] / trio_point_price_map[symbol_name] * 3
    # 出现次数最多的ts
    ts_counter = Counter(ts_list)
    most_common_ts = ts_counter.most_common(1)[0][0]
    # TODO 返回结果根据调用情况再考虑一下
    data = {
        'combination_id': combination.id, 'combined_method': mode,
        'symbol_3point_price': trio_point_price_map,
        'combination_3point_price': calculate_combination_3point_price(combination),
        'interval': first_interval,
        'combination_price': [combination.name, most_common_ts, open_combo_price, high_combo_price,
                              low_combo_price, closed_combo_price]
    }
    return True, data


# 使用strict_match方式来使用传入的symbol_rates_list和combination生成组合价格
# https://trello.com/c/oI5VMqx8
def cal_comb_price_strict_match(symbol_rates_list, combination_id):
    combination = Combination.get_by_id(combination_id)
    symbols = Symbol.select().where(Symbol.id.in_(combination.symbol_list.split(",")))
    trio_point_price_map = {}  # 3点价格
    for symbol in symbols:
        print(model_to_dict(symbol))
        if symbol.trio_point_price is None:
            logger.error("缺少3点价格数据：symbol=%s", symbol.name)
            return False, None
        trio_point_price_map[symbol] = symbol.trio_point_price

    open_price_map = {}
    high_price_map = {}
    low_price_map = {}
    closed_price_map = {}
    interval = 60 * 60  # 默认1小时
    # 检查对应组合中的symbol是否都有报价，并记录最小和最大的时间戳
    min_ts = -1  # 最小的时间戳
    max_ts = -1  # 最大的时间戳
    ts_list = []
    for symbol in symbols:
        # print("check=>", symbol.name)
        symbol_name = symbol.name
        # 同symbol的，取最前的一条报价
        find = False
        for sub_list in symbol_rates_list:
            for item in sub_list:
                if item['symbol'] == symbol_name:
                    # print(item)
                    find = True
                    # 计算 价格/3点价*3
                    open_price_map[symbol_name] = Decimal.from_float(item['value'][2]) / trio_point_price_map[
                        symbol_name] * 3
                    high_price_map[symbol_name] = Decimal.from_float(item['value'][3]) / trio_point_price_map[
                        symbol_name] * 3
                    low_price_map[symbol_name] = Decimal.from_float(item['value'][4]) / trio_point_price_map[
                        symbol_name] * 3
                    closed_price_map[symbol_name] = Decimal.from_float(item['value'][5]) / trio_point_price_map[
                        symbol_name] * 3
                    if item['interval'] == '1m':
                        interval = 60
                    ts = item['value'][1]
                    ts_list.append(ts)
                    if min_ts == -1 or ts < min_ts:
                        min_ts = ts
                    if max_ts == -1 or ts > max_ts:
                        max_ts = ts
                    break
            if find:
                # print("----------")
                break
        if not find:
            logger.error("symbol报价缺失：%s", symbol_name)
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
    ts_counter = Counter(ts_list)
    most_common_ts = ts_counter.most_common(1)[0][0]
    # print(ts_list, ts_counter.most_common(1), ts_counter.most_common(1)[0][0])
    data = {
        'combination_id': combination_id, 'combined_method': 'strict_match',
        'symbol_3point_price': trio_point_price_map,
        'combination_3point_price': calculate_combination_3point_price(combination),
        'interval': '1m' if interval == 60 else '1h',
        'combination_price': [combination.name, most_common_ts, open_combo_price, high_combo_price,
                              low_combo_price, closed_combo_price]
    }
    return True, data


# best_effort_match模式计算组合价，https://trello.com/c/rZybjVKC
def cal_comb_price_best_effort_match(symbol_rates_list, combination_id, db):
    pass


# 从db中拉取特定symbol到指定时间戳之前的最新报价
def get_lastest_price_before_dst_ts(db, interval, symbol, dst_ts):
    tbl = get_model_table_by_symbol(symbol)
    sql = "select symbol_name, ts, price_open, price_high, price_low, price_closed " \
          "from original_data_source.%s where `interval`='%s' and ts<=%d order by ts desc limit 1" % (
              tbl, interval, dst_ts)
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result
