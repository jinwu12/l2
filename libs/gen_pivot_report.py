from libs.database import *

logger = commons.create_logger()


def update_historical_pivot_report(combination, default_column=4):
    """
    为指定的Combination生成从特定时间点开始（默认为该Combination最早的组合价格数据的时间戳的时间），生成到最新的时间戳为止的日线行情记录表。
    - 本程序只能在休市日运行
    - 本程序需要在日线行情记录表的前至少运行一次
    :param combination: 待生成行情记录表的Combination对象
    :param default_column: 初始记录栏目，默认为下降趋势栏4
    :return:
    """
    pass


def record_check(price, table_name):
    """
    在确认不需要切换记录栏后，需要判断该日价格的“是否记录”取值是1或者是0
    :param price: 待判断是否要记录的价格
    :param table_name: 待插入的表名，用于获取当前最新记录栏及最新的有记录价格
    :return: True/False
    """
    pass


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
