from enum import IntEnum, unique

from libs.database import *


@unique
class PivotReportColumn(IntEnum):
    """行情记录表栏目枚举"""
    # 次级回升
    SECONDARY_RALLY = 1
    # 自然回升
    NATURAL_RALLY = 2
    # 上升趋势
    UPWARD_TREND = 3
    # 下降趋势
    DOWNWARD_TREND = 4
    # 自然回撤
    NATURAL_REACTION = 5
    # 次级回撤
    SECONDARY_REACTION = 6


def update_historical_pivot_report(combination, default_column=PivotReportColumn.DOWNWARD_TREND):
    """
    为指定的Combination生成从特定时间点开始（默认为该Combination最早的组合价格数据的时间戳的时间），生成到最新的时间戳为止的日线行情记录表。
    - 本程序只能在休市日运行
    - 本程序需要在日线行情记录表的前至少运行一次
    :param combination: 待生成行情记录表的Combination对象
    :param default_column: 初始记录栏目，默认为下降趋势栏
    :return:
    """
    pass


def price_need_record(price, pivot_report, default_column=PivotReportColumn.DOWNWARD_TREND):
    """
    判断价格是否需要记录，对应需求为：https://trello.com/c/zVFRorLF
    :param price: 待判断是否要记录的价格
    :param pivot_report: pivot_report编号，用于获取当前最新记录栏及最新的有记录价格
    :param default_column: 初始记录栏目，默认为下降趋势栏
    :return: True/False
    """
    # 先判断是否有数据，有则取ts最大的
    # 没有则以默认栏计算
    latest_column = default_column
    latest_price = price
    # 取最新的且有记录的数据
    records = PivotReportRecord.select().where(PivotReportRecord.pivot_report == pivot_report,
                                               PivotReportRecord.is_recorded == True).order_by(
        PivotReportRecord.date.desc()).limit(1).execute()
    if len(records) > 0:
        record = records[0]
        try:
            latest_column = PivotReportColumn(record.recorded_column)
        except ValueError:  # 值非法，使用默认值
            pass
        latest_price = record.price
    if latest_column == PivotReportColumn.NATURAL_RALLY:
        return True if price >= latest_price else False
    elif latest_column == PivotReportColumn.UPWARD_TREND:
        return True if price >= latest_price else False
    elif latest_column == PivotReportColumn.DOWNWARD_TREND:
        return False if price > latest_price else True
    elif latest_column == PivotReportColumn.NATURAL_REACTION:
        return False if price > latest_price else True
    elif latest_column == PivotReportColumn.SECONDARY_RALLY:
        return True if price >= latest_price else False
    elif latest_column == PivotReportColumn.SECONDARY_REACTION:
        return False if price > latest_price else True
    else:
        raise Exception("当前不支持的栏目逻辑：%s" % str(latest_column))

def get_combination_symbol_timezone(combination_id):
    '''
    根据combination id，获取组成该combination的symbol的所有时区列表，用于生成属于该时区对应的日线行情记录表。
    :param combination_id: 待获取时区的组合ID
    ：return：{'combination_timezone':该组合ID去重后的时区列表}
    '''
    try:
        combination = Combination.get(Combination.id == combination_id)
    except:
        logger.error("缺少对应combination的行情数据：combo_id=%s", combination_id)
        return None
    # 根据symbol ID到Tbl_symbol_method中获取对应的时区
    else:
        tz = []
        for symbolid in combination.symbol_list.split(","):
            ts = Symbol.get(Symbol.id == int(symbolid))
            tz.append(ts.timezone)
        # 去除重复元素
        tz = list(set(tz))
        result = {'combination_timezone': tz}
        return result