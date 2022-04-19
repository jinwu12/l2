from enum import IntEnum, unique

from libs import commons
from libs.database import *
from libs.database import PivotReportRecord

logger = commons.create_logger()


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
    record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == pivot_report,
                                              PivotReportRecord.is_recorded == True).order_by(
        PivotReportRecord.date.desc()).limit(1).get_or_none()
    if record is not None:
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


def determine_column(latest_prr, current_price, trio_point_price):
    """
    栏目切换
    :param latest_prr:  最新的行情记录
    :param current_price: 当前价格
    :param trio_point_price: 3点价格
    :return:
    """
    latest_column = PivotReportColumn(latest_prr.recorded_column)
    target_column = None
    mute_count = 0  # 切换次数
    if latest_column == PivotReportColumn.NATURAL_RALLY:
        # 传入价格（今日收盘价）比自然回升栏（2）最新一个关键点价格高3点或更多则切换到上升趋势栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_RALLY,
                                                  PivotReportRecord.is_pivot == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and current_price - record.price >= 3:
            mute_count += 1
            target_column = PivotReportColumn.UPWARD_TREND
        # 传入价格（今日收盘价）比上升趋势栏（3）最新一条有记录的价格高则切换到上升趋势栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.UPWARD_TREND
                                                  ).order_by(PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and current_price - record.price >= 3:
            mute_count += 1
            target_column = PivotReportColumn.UPWARD_TREND
        # 今日的收盘价比自然回升栏最新一条有记录的价格低6点或以上，但并没有低于自然回撤栏中但最新一个有记录的价格，则切换到次级回撤栏
        record1 = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                   PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_RALLY,
                                                   PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        record2 = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                   PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_REACTION,
                                                   PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record1 is not None and record2 is not None and record1.price - current_price >= 6 \
                and current_price >= record2.price:
            mute_count += 1
            target_column = PivotReportColumn.SECONDARY_REACTION
        # 今日收盘价比自然回升栏最新一条有记录的价格低了6点或更多则切换到自然回撤栏
        if record1 is not None and record1.price - current_price >= 6:
            mute_count += 1
            target_column = PivotReportColumn.NATURAL_REACTION
    elif latest_column == PivotReportColumn.NATURAL_REACTION:
        # 传入价格（今日收盘价）比自然回撤栏（5）最新一个关键点的价格低3点或更多则切换到下降趋势栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_REACTION,
                                                  PivotReportRecord.is_pivot == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and record.price - current_price >= 3:
            mute_count += 1
            target_column = PivotReportColumn.DOWNWARD_TREND
        # 传入价格（今日收盘价）比下降趋势栏（4）的最新一条有记录的价格低则切换到下降趋势栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.DOWNWARD_TREND,
                                                  PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and record.price > current_price:
            mute_count += 1
            target_column = PivotReportColumn.DOWNWARD_TREND
        # 今日收盘价比自然回撤栏的最新一条有记录的价格高6点或以上，但并没有超过自然回升栏的最新一个有记录的价格，切换至次级回升栏
        record1 = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                   PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_REACTION,
                                                   PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        record2 = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                   PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_RALLY,
                                                   PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record1 is not None and record2 is not None and current_price - record1.price >= 6 \
                and current_price <= record2.price:
            mute_count += 1
            target_column = PivotReportColumn.SECONDARY_RALLY
        # 今日收盘价比自然回撤栏最新一条记录的价格高6点或更多则切换到自然回升栏
        if record1 is not None and current_price - record1.price >= 6:
            mute_count += 1
            target_column = PivotReportColumn.NATURAL_RALLY
    elif latest_column == PivotReportColumn.SECONDARY_RALLY:
        # 今日收盘价比自然回升栏最后一个有记录的价格高则切换到自然回升栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_RALLY,
                                                  PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and current_price > record.price:
            mute_count += 1
            target_column = PivotReportColumn.NATURAL_RALLY
        # 今日收盘价比自然回撤栏最后一个有记录的价格低则切换到自然回撤栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_REACTION,
                                                  PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and current_price < record.price:
            mute_count += 1
            target_column = PivotReportColumn.NATURAL_REACTION
    elif latest_column == PivotReportColumn.SECONDARY_REACTION:
        # 今日收盘价比自然回撤栏最后一个有记录的价格低则切换到自然回撤栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_REACTION,
                                                  PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and current_price < record.price:
            mute_count += 1
            target_column = PivotReportColumn.NATURAL_REACTION
        # 今日收盘价比自然回升栏最后一个有记录的价格高则切换到自然回升栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.NATURAL_RALLY,
                                                  PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and current_price > record.price:
            mute_count += 1
            target_column = PivotReportColumn.NATURAL_RALLY
    elif latest_column == PivotReportColumn.UPWARD_TREND:
        # 今日收盘价比上升趋势栏最新一条有记录的价格低6点或以上则切换到自然回撤栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.UPWARD_TREND,
                                                  PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and record.price - current_price >= 6:
            mute_count += 1
            target_column = PivotReportColumn.NATURAL_REACTION
    elif latest_column == PivotReportColumn.DOWNWARD_TREND:
        # 今日收盘价比下降趋势栏最新一条有记录的价格高6点或更多则切换到自然回升栏
        record = PivotReportRecord.select().where(PivotReportRecord.pivot_report == latest_prr.pivot_report,
                                                  PivotReportRecord.recorded_column == PivotReportColumn.DOWNWARD_TREND,
                                                  PivotReportRecord.is_recorded == True).order_by(
            PivotReportRecord.date.desc()).limit(1).get_or_none()
        if record is not None and record.price - current_price >= 6:
            mute_count += 1
            target_column = PivotReportColumn.NATURAL_RALLY
    return target_column


def get_combination_symbol_timezone(combination_id):
    """
    根据combination id，获取组成该combination的symbol的所有时区列表，用于生成属于该时区对应的日线行情记录表。
    :param combination_id: 待获取时区的组合ID
    ：return：{'combination_timezone':该组合ID去重后的时区列表}
    """
    try:
        combination = Combination.get_by_id(combination_id)
    except:
        logger.error("缺少对应combination的行情数据：combo_id=%s", combination_id)
        return None
    # 根据symbol ID到Tbl_symbol_method中获取对应的时区
    else:
        tz = []
        for symbol_id in combination.symbol_list.split(","):
            symbol = Symbol.get_by_id(int(symbol_id))
            if symbol.timezone not in tz:
                tz.append(symbol.timezone)
        result = {'combination_timezone': tz}
        return result


def update_pivot_point(src_column, dst_column, pivot_report):
    """
    实时行情记录表根据更新关键点的判断规则，在符合规则时更新历史价格为关键点
    :param src_column：源记录栏
    :param dst_column：目标记录栏
    :param pivot_report: pivot_report编号，用于获取当前最新记录栏及最新的有记录价格
    :return:{
            'result':True/False,
            'pivot_point_column': 更新的关键点所在记录栏
            'pivot_point_date':更新的关键点的日期
             }
    """
    result = False
    pivot_point_column = 0
    pivot_point_date = ''
    # 获取源记录栏最新的记录
    records = PivotReportRecord.select().where(PivotReportRecord.pivot_report == pivot_report,
                                               PivotReportRecord.is_recorded == True,
                                               PivotReportRecord.recorded_column == src_column).order_by(
        PivotReportRecord.date.desc()).limit(1).execute()
    if len(records) > 0:
        record = records[0]
        if src_column == PivotReportColumn.NATURAL_RALLY and dst_column == PivotReportColumn.NATURAL_REACTION:
            result = True
        elif src_column == PivotReportColumn.UPWARD_TREND and dst_column == PivotReportColumn.NATURAL_REACTION:
            result = True
        elif src_column == PivotReportColumn.DOWNWARD_TREND and dst_column == PivotReportColumn.NATURAL_RALLY:
            result = True
        elif src_column == PivotReportColumn.NATURAL_REACTION and dst_column == PivotReportColumn.NATURAL_RALLY:
            result = True
        if result:
            pivot_point_column = src_column
            pivot_point_date = time.strftime("%Y-%m-%d", record.data)
            return {
                'result': result,
                'pivot_point_column': pivot_point_column,
                'pivot_point_date': pivot_point_date
            }


def update_historical_pivot_point(src_column, dst_column, pivot_report, latest_ts):
    """
    历史行情记录表根据更新关键点的判断规则，在符合规则时更新历史价格为关键点
    :param src_column：源记录栏
    :param dst_column：目标记录栏
    :param pivot_report: pivot_report编号，用于获取当前最新记录栏及最新的有记录价格
    :param latest_ts 历史数据时间戳，更新时间戳之前的关键点
    :return:{
            'result':True/False,
            'pivot_point_column': 更新的关键点所在记录栏
            'pivot_point_date':更新的关键点的日期
             }
    """
    result = False
    pivot_point_column = 0
    pivot_point_date = ''
    # 获取源记录栏在时间戳以前的最新记录
    records = PivotReportRecord.select().where(PivotReportRecord.pivot_report == pivot_report,
                                               PivotReportRecord.is_recorded == True,
                                               PivotReportRecord.recorded_column == src_column,
                                               PivotReportRecord.date < latest_ts).order_by(
        PivotReportRecord.date.desc()).limit(1).execute()
    if len(records) > 0:
        record = records[0]
        if src_column == PivotReportColumn.NATURAL_RALLY and dst_column == PivotReportColumn.NATURAL_REACTION:
            result = True
        elif src_column == PivotReportColumn.UPWARD_TREND and dst_column == PivotReportColumn.NATURAL_REACTION:
            result = True
        elif src_column == PivotReportColumn.DOWNWARD_TREND and dst_column == PivotReportColumn.NATURAL_RALLY:
            result = True
        elif src_column == PivotReportColumn.NATURAL_REACTION and dst_column == PivotReportColumn.NATURAL_RALLY:
            result = True
        if result:
            pivot_point_column = src_column
            pivot_point_date = time.strftime("%Y-%m-%d", record.data)
            return {
                'result': result,
                'pivot_point_column': pivot_point_column,
                'pivot_point_date': pivot_point_date
            }
