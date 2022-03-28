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
            tbl = get_model_table_by_symbol_value(symbol.symbol_value)
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
    """
    计算组合价格
    :param symbol_rates_list: 同一个时间戳的不同symbol的dict报价列表
    :param combination: 组合数据对象
    :param mode: strict_match或者best_effort，strict_match参考：https://trello.com/c/oI5VMqx8，best_effort参考：https://trello.com/c/rZybjVKC
    :return:
    """
    modes = ['strict_match', 'best_effort_match']
    if mode not in modes:
        logger.error("目前只支持%s，暂时不支持%s", modes, mode)
        return False, None
    if mode == modes[0]:
        return calc_combo_price_strict_match(symbol_rates_list, combination)
    else:
        return calc_combo_price_best_effort_match(symbol_rates_list, combination)


# strict_match模式计算组合价，https://trello.com/c/oI5VMqx8
def calc_combo_price_strict_match(symbol_rates_list, combination):
    """
        使用strict_match模式计算组合价格
        :param symbol_rates_list: 同一个时间戳的不同symbol的dict报价列表
        :param combination: 组合数据对象
        :return:
    """
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
            logger.error("计算组合价格时缺少对应symbol数据：combo_id=%s, symbol_list=%s, 缺少%s", combination.id,
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
        symbol_value = item['symbol']
        ts_list.append(item['ts'])
        # 计算 价格/3点价*3
        open_combo_price += item['price_open'] / trio_point_price_map[symbol_value] * 3
        high_combo_price += item['price_high'] / trio_point_price_map[symbol_value] * 3
        low_combo_price += item['price_low'] / trio_point_price_map[symbol_value] * 3
        closed_combo_price += item['price_closed'] / trio_point_price_map[symbol_value] * 3
    # 出现次数最多的ts
    ts_counter = Counter(ts_list)
    most_common_ts = ts_counter.most_common(1)[0][0]
    # TODO 返回结果根据调用情况再考虑一下
    data = {
        'combination_id': combination.id, 'combined_method': 'strict_match',
        'symbol_3point_price': trio_point_price_map,
        'combination_3point_price': calculate_combination_3point_price(combination),
        'interval': first_interval,
        'combination_price': [combination.name, most_common_ts, open_combo_price, high_combo_price,
                              low_combo_price, closed_combo_price]
    }
    return True, data


# best_effort_match模式计算组合价，https://trello.com/c/rZybjVKC
def calc_combo_price_best_effort_match(symbol_rates_list, combination):
    """
           使用best_effort模式计算组合价格
           :param symbol_rates_list: 同一个时间戳的不同symbol的dict报价列表
           :param combination: 组合数据对象
           :return:
       """
    candidate_rates_list = []  # 候选数据(属于组合中的成员symbol报价)
    lack_symbols = []  # best_effort模式下，缺数据需要取临近数据补的symbol value列表
    trio_point_price_map = {}  # 3点价格
    valid_ts_list = []  # 有效数据的ts列表，用来取出现最多的ts
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
                candidate_rates_list.append(rate)
                valid_ts_list.append(rate['ts'])
                found = True
                break
        if not found:
            lack_symbols.append(symbol.symbol_value)
    if len(candidate_rates_list) == 0:
        logger.error("best_effort模式下没有有效的候选数据：combination=%, symbol_rates_list=%s", combination, symbol_rates_list)
        return False, None
    # 出现次数最多的ts
    ts_counter = Counter(valid_ts_list)
    most_common_ts = ts_counter.most_common(1)[0][0]
    first_rate = candidate_rates_list[0]
    first_interval = first_rate['interval']
    if len(lack_symbols) > 0:
        for symbol_value in lack_symbols:
            rate = get_lastest_price_before_dst_ts(symbol_value, first_interval, most_common_ts)
            if rate:
                candidate_rates_list.append(rate)
            else:
                logger.error("计算组合价格时缺少对应symbol数据(ts<=%d)：combo_id=%s, symbol_list=%s, 缺少%s", most_common_ts,
                             lack_symbols,
                             combination.symbol_list, symbol_value)
                return False, None

    valid_rates_list = []

    max_gap = 60 if first_interval == '1m' else 60 * 60  # 1个interval的时间间隔
    # 评估评估候选数据的时间差，看是否需要另拉数据
    for rate in candidate_rates_list:
        if rate['interval'] != first_interval:
            logger.error("提供的数据interval不一致：%s", candidate_rates_list)
            return False, None
        elif abs(most_common_ts - rate['ts']) > max_gap and rate['symbol'] not in lack_symbols:  # 重拉数据
            rate = get_lastest_price_before_dst_ts(rate['symbol'], first_interval, most_common_ts)
            if rate:
                valid_rates_list.append(rate)
            else:
                logger.error("计算组合价格时缺少对应symbol数据(ts<=%d)：combo_id=%s, symbol_list=%s, 缺少%s", most_common_ts,
                             rate['symbol'], combination.symbol_list, symbol_value)
                return False, None
        else:
            valid_rates_list.append(rate)

    # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
    open_combo_price = 0
    high_combo_price = 0
    low_combo_price = 0
    closed_combo_price = 0
    for item in valid_rates_list:
        symbol_value = item['symbol']

        # 计算 价格/3点价*3
        open_combo_price += item['price_open'] / trio_point_price_map[symbol_value] * 3
        high_combo_price += item['price_high'] / trio_point_price_map[symbol_value] * 3
        low_combo_price += item['price_low'] / trio_point_price_map[symbol_value] * 3
        closed_combo_price += item['price_closed'] / trio_point_price_map[symbol_value] * 3

    # TODO 返回结果根据调用情况再考虑一下
    data = {
        'combination_id': combination.id, 'combined_method': 'best_effort_match',
        'symbol_3point_price': trio_point_price_map,
        'combination_3point_price': calculate_combination_3point_price(combination),
        'interval': first_interval,
        'combination_price': [combination.name, most_common_ts, open_combo_price, high_combo_price,
                              low_combo_price, closed_combo_price]
    }
    return True, data


# 从db中拉取特定symbol到指定时间戳之前(包含当前)的最新报价
def get_lastest_price_before_dst_ts(symbol_value, interval, dst_ts):
    tbl = get_model_table_by_symbol_value(symbol_value)
    sql = "select symbol_name as symbol, `interval`, ts, price_open, price_high, price_low, price_closed " \
          "from original_data_source.%s where `interval`='%s' and ts<=%d order by ts desc limit 1" % (
              tbl, interval, dst_ts)
    cursor = data_source_db.execute_sql(sql)
    result = cursor.fetchone()
    if result:
        column_names = [x[0] for x in cursor.description]
        return dict(zip(column_names, result))  # 封装成dicts返回
