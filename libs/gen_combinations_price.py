import traceback
from collections import Counter

from libs.database import *

logger = commons.create_logger()


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
def get_historical_symbol_rates_list(symbol_ids, start_ts, end_ts, interval):
    """
    获取指定指定时间戳区间内同属一个组合的几个汇率数据
    :param symbol_ids:  汇率id列表，一般同属于一个组合
    :param start_ts:  开始时间戳
    :param end_ts: 结束时间戳
    :param interval: 间隔，1m或1h
    :return: [
        [symbol1@时间戳1的报价dict, symbol2@时间戳1的报价dict, ...],
        [symbol1@时间戳2的报价dict, symbol2@时间戳2的报价dict, ...],
        ...
        ]
    """
    start_ts = commons.check_and_fix_timestamp(start_ts, interval)
    end_ts = commons.check_and_fix_timestamp(end_ts, interval)
    data = {}
    symbols = Symbol.select().where(Symbol.id.in_(symbol_ids))
    for symbol in symbols:
        # print(symbol)
        try:
            tbl = get_model_table_by_symbol_value(symbol.symbol_value)
            # print(tbl)
            sql = "select symbol_name as symbol, `interval`, ts, price_open, price_high, price_low, price_closed from original_data_source.%s " \
                  "where `interval`='%s' and ts between %d and %d order by ts" % (
                      tbl, interval, start_ts, end_ts)
            cursor = data_source_db.execute_sql(sql)
            column_names = [x[0] for x in cursor.description]
            result = [dict(zip(column_names, row)) for row in cursor.fetchall()]

            exist = data.get(symbol.name)
            if exist is None:
                data[symbol.name] = result
            else:
                data[symbol.name] = exist + result
        except:
            logger.error(traceback.format_exc())

    # 组织返回结果
    # print(data)
    result = []
    ts = start_ts
    while ts <= end_ts:
        data_in_same_ts = []
        for symbol in symbols:
            data_list = data.get(symbol.name)
            if data_list is not None and len(data_list) > 0 and data_list[0]['ts'] == ts:
                data_in_same_ts.append(data_list[0])
                del data_list[0]
        if len(data_in_same_ts) > 0:
            result.append(data_in_same_ts)
        else:
            logger.warning("组合(%s)在%s(%d)缺数据", symbol_ids, commons.timestamp_to_datetime_str(ts), ts)
        if "1m" == interval:
            ts += 60
        elif "1h" == interval:
            ts += 60 * 60
    # print(result)
    return result


def calc_combo_price(symbol_rates_list, combination):
    """
    计算组合价格
    :param symbol_rates_list: 同一个时间戳的不同symbol的dict报价列表
    :param combination: 组合数据对象
    :return:
    """
    modes = ['strict_match', 'best_effort_match']
    if combination.combined_method not in modes:
        logger.error("目前只支持%s，暂时不支持%s", modes, combination.combined_method)
        return False, None
    if combination.combined_method == modes[0]:
        return calc_combo_price_strict_match(symbol_rates_list, combination)
    else:
        return calc_combo_price_best_effort_match(symbol_rates_list, combination)


# strict_match模式计算组合价，https://trello.com/c/oI5VMqx8
def calc_combo_price_strict_match(symbol_rates_list, combination):
    """
        使用strict_match模式计算组合价格
        :param symbol_rates_list: 同一个时间戳的不同symbol的dict报价列表
        :param combination: 组合数据对象
        :return: CombinedSymbol
    """
    valid_rates_list = []  # 最终用来计算的数据
    trio_point_price_map = {}  # 3点价格
    # 判断symbol_rates_list是否包含组合要求的所有symbol的数据
    for symbol_id in combination.symbol_list.split(','):
        symbol = global_cache.get_symbol_by_id(int(symbol_id))
        if symbol is None:
            logger.error("不存在对应id的symbol：id=%s", symbol_id)
            return None
        elif symbol.trio_point_price is None:
            logger.error("缺少3点价格数据：symbol=%s", symbol.name)
            return None
        symbol_value = symbol.symbol_value
        trio_point_price_map[symbol_value] = float(symbol.trio_point_price)
        found = False
        for rate in symbol_rates_list:
            if rate['symbol'] == symbol_value:
                valid_rates_list.append(rate)
                found = True
                break
        if not found:
            logger.error("计算组合价格时缺少对应symbol的行情数据：combo_id=%s, symbol_list=%s, 缺少%s", combination.id,
                         combination.symbol_list, symbol_value)
            return None
    first_rate = valid_rates_list[0]
    first_ts = first_rate['ts']
    first_interval = first_rate['interval']
    max_gap = 60 if first_interval == '1m' else 60 * 60  # 1个interval的时间间隔
    min_ts = first_ts
    max_ts = first_ts
    for item in valid_rates_list[1:]:
        if item['interval'] != first_interval:
            logger.error("提供的数据interval不一致：%s", valid_rates_list)
            return None
        ts = item['ts']
        if first_ts != ts:
            min_ts = min_ts if min_ts <= ts else ts
            max_ts = max_ts if max_ts >= ts else ts
    # 判断所有时间戳是否一致
    gap = max_ts - min_ts
    if gap > max_gap:
        logger.error("提供的数据时差超过1个interval：%s", valid_rates_list)
        return None
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
    result = dict(symbol=generate_combination_name(combination), ts=most_common_ts, interval=first_interval,
                  price_open=open_combo_price,
                  price_high=high_combo_price, price_low=low_combo_price, price_closed=closed_combo_price)
    return result


# best_effort_match模式计算组合价，https://trello.com/c/rZybjVKC
def calc_combo_price_best_effort_match(symbol_rates_list, combination):
    """
           使用best_effort模式计算组合价格
           :param symbol_rates_list: 同一个时间戳的不同symbol的dict报价列表
           :param combination: 组合数据对象
           :return: CombinedSymbol
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
            return None
        elif symbol.trio_point_price is None:
            logger.error("缺少3点价格数据：symbol=%s", symbol.name)
            return None
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
        return None
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
                return None

    valid_rates_list = []

    max_gap = 60 if first_interval == '1m' else 60 * 60  # 1个interval的时间间隔
    # 评估评估候选数据的时间差，看是否需要另拉数据
    for rate in candidate_rates_list:
        if rate['interval'] != first_interval:
            logger.error("提供的数据interval不一致：%s", candidate_rates_list)
            return None
        elif abs(most_common_ts - rate['ts']) > max_gap and rate['symbol'] not in lack_symbols:  # 重拉数据
            rate = get_lastest_price_before_dst_ts(rate['symbol'], first_interval, max(valid_ts_list))  # 这里要取最大的ts
            if rate:
                valid_rates_list.append(rate)
            else:
                logger.error("计算组合价格时缺少对应symbol数据(ts<=%d)：combo_id=%s, symbol_list=%s, 缺少%s", most_common_ts,
                             rate['symbol'], combination.symbol_list, symbol_value)
                return None
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

    result = dict(symbol=generate_combination_name(combination), ts=most_common_ts, interval=first_interval,
                  price_open=open_combo_price,
                  price_high=high_combo_price, price_low=low_combo_price, price_closed=closed_combo_price)
    return result


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


def generate_combination_name(combination):
    """
    生成组合价格行情的symbol名
    :param combination: 组合基础配置
    :return:   成员symbol name+组合方法+3点价格+trading_symbol
    """
    result = ''
    for symbol_id in combination.symbol_list.split(","):
        result += global_cache.get_symbol_by_id(int(symbol_id)).name + '_'
    result += combination.combined_method + '_' + str(
        combination.combination_3point_price) + '_' + combination.trading_symbol
    return result


def update_historical_combined_data(interval, start, end, combination_ids=[]):
    """
    历史组合价格入库(https://trello.com/c/W0V15uid)
    :param interval: 1m或1h
    :param start: 开始时间
    :param end: 结束时间
    :param combination_ids: 指定要生成的组合id列表
    :return:
    """
    combinations = Combination.select()
    if len(combination_ids) > 0:
        combinations = Combination.select().where(Combination.id.in_(combination_ids))
    for combination in combinations:
        data = get_historical_symbol_rates_list(combination.symbol_list.split(","),
                                                start.timestamp(), end.timestamp(), interval)
        result = []
        for sub_list in data:
            # print(sub_list)
            item = calc_combo_price(sub_list, combination)
            if item:
                result.append(item)
                # item.save()
        # 批量入库
        if len(result) > 0:
            CombinedSymbol.replace_many(result).execute()
