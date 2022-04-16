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
