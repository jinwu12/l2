from configparser import ConfigParser

from abc import abstractmethod
from peewee import *
import mysql.connector
from libs import commons

cfg = ConfigParser()
cfg.read('./config.ini')
db_host = cfg.get('database', 'host')
db_user = cfg.get('database', 'user')
db_passwords = cfg.get('database', 'passwords')

################################################
config_db = MySQLDatabase(
    'Global_Config', host=db_host, user=db_user, passwd=db_passwords, port=3306
)


# 信号类型对象，存储在Global_config中
class SignalType(Model):
    # 自增ID
    id = AutoField(column_name='id', primary_key=True)
    # 信号名称
    signal_name = CharField(
        column_name='signal_name', max_length=16, null=False
    )
    # 信号方向
    direction = CharField(column_name='direction', max_length=8, null=False)
    # 备注
    comments = TextField(column_name='comments')

    # 存放在Global_Config库中
    class Meta:
        database = config_db
        table_name = 'signal_type'
        indexes = (
            (('signal_name', 'direction'), True),
        )


# PivotReport基础对象
class PivotReport(Model):
    # 自增ID
    id = AutoField(column_name='id', primary_key=True)
    # 行情记录表的初始记录栏目，默认值为4
    initial_column = SmallIntegerField(column_name='initial_column', default=4)
    # 行情记录表对应的combination id
    combination_id = BigIntegerField(column_name='combination_id', null=False)
    # 行情记录表对应的combination下的symbol对应时区的名称
    timezone = CharField(column_name='timezone', max_length=16, null=False)
    # 组合方法，行情记录表对应的combination下的combined_method
    combined_method = CharField(
        column_name='combined_method',  max_length=16, null=False
    )
    # 开始记录时间，默认值应为combination最早有记录的时间, 以utc0时区的时间戳存储
    start_date = BigIntegerField(column_name='start_date', null=False)
    # 备注
    comments = TextField(column_name='comments')

    # 存放在config_db中
    class Meta:
        database = config_db
        table_name = "pivot_reports"
        indexes = (
            (
                (
                    "initial_column",
                    "combination_id",
                    "timezone",
                    "start_date"
                ),
                True
            ),
        )


# combination基础数据
class Combination(Model):
    id = AutoField(column_name='id', primary_key=True)
    # 组合名称，默认为空。当为空时通过symbol list中的symbol组合来生成
    name = CharField(
        unique=True, column_name='combination_name', max_length=256)
    # 组合价格的symbol列表，半角逗号分隔
    symbol_list = CharField(column_name='symbol_list', max_length=128)
    # 组合价格匹配方式，strict_match或者best_effort_match
    combined_method = CharField(column_name='combined_method', max_length=64)
    # 组合价格3点取值，默认为0（即为symbol数量*3）
    combination_3point_price = SmallIntegerField(
        column_name='combination_3point_price')
    # 备注字段
    comments = TextField(column_name='comments')
    # 该组合用于交易的品类，允许多个，用半角逗号分隔
    trading_symbol = CharField(column_name='trading_symbol', max_length=256)

    # 组合配置依然存放在config_db中
    class Meta:
        database = config_db
        table_name = "symbol_combinations"


# 使用的各平台账号信息
class AccountInfo(Model):
    id = AutoField(column_name="account_id", primary_key=True)
    name = CharField(unique=True, column_name="account_name", max_length=128)
    platform = CharField(column_name="account_platform", max_length=64)
    server = CharField(column_name="account_server", max_length=128)
    password = CharField(column_name="account_pass", max_length=128)
    description = TextField(column_name="desciption")

    class Meta:
        database = config_db
        table_name = "account_info"


# symbol基础数据
class Symbol(Model):
    id = AutoField(column_name="method_id", primary_key=True)
    name = CharField(unique=True, column_name="symbol_name", max_length=16)
    # 对应程序抓取方法的名称
    method = CharField(column_name="method_name", max_length=128)
    comments = TextField()
    timezone = CharField(max_length=128)
    symbol_value = CharField(max_length=16)
    contract_size = CharField(max_length=32)
    digits = SmallIntegerField()
    trio_point_price = DecimalField(column_name="3point_price", max_digits=10)

    class Meta:
        database = config_db
        table_name = "Tbl_symbol_method"


###############################################
# 已产生的信号对象，存放在production_signal库中
production_signal_db = MySQLDatabase(
    'production_signal',
    host=db_host,
    user=db_user,
    passwd=db_passwords,
    port=3306
    )


class Signal(Model):
    # 自增ID
    id = AutoField(column_name='id', primary_key=True)
    # 信号所在的行情记录表
    pivot_report_id = BigIntegerField(
        column_name='pivot_report_id', null=False)
    # 信号发生的时间点，以utc0时间戳记录
    ts = BigIntegerField(column_name='ts', null=False)
    # 信号发生时的所在记录栏
    occurred_column = SmallIntegerField(
        column_name='occurred_column', null=False)
    # 信号发生时的价格，需要取该时间点的开盘价
    price = DoubleField(column_name='price', null=False)
    # 该信号是否已被确认
    is_confirmed = BooleanField(column_name='is_confirmed', null=False)
    # 该信号的类型
    signal_type = BigIntegerField(column_name='signal_type', null=False)

    class Meta:
        database = production_signal_db
        table_name = 'signal_data'


###############################################
# 行情记录表数据存放在production_pivot_report库中
production_pivot_report_db = MySQLDatabase(
    'production_pivot_report',
    host=db_host,
    user=db_user,
    passwd=db_passwords,
    port=3306
    )

# 行情记录表的每日记录类


class PivotReportRecord(Model):
    # 自增ID
    id = AutoField(column_name="id", primary_key=True)
    # 行情记录属于哪一个行情记录表
    pivot_report = BigIntegerField(column_name='pivot_report_id', null=False)
    # 行情记录的日期，以行情记录表的时区所对应的当日0点0分0秒的时间戳来记录,作为该记录的日期
    date = BigIntegerField(column_name='date', null=False)
    # 行情记录的价格，取date所在当天的23时收盘价作为当天的收盘价记录
    price = DoubleField(column_name='price', null=False)
    # 该记录是否需要在当天的结果报表中记录
    is_recorded = BooleanField(null=False)
    # 该记录处于结果报表中的哪一栏,取值范围如下：
    '''
    - 次级回升栏:1
    - 自然回升栏:2
    - 上升趋势栏:3
    - 下降趋势栏:4
    - 自然回撤栏:5
    - 次级回撤栏:6
    '''
    recorded_column = SmallIntegerField(
        column_name='recorded_column', null=False)
    # 该记录点是否属于关键点
    is_pivot = BooleanField(null=False)

    # 数据存放在production_pivot_report中
    class Meta:
        database = production_pivot_report_db
        table_name = 'pivot_report_price'


###############################################
data_source_db = MySQLDatabase(
    'original_data_source',
    host=db_host,
    user=db_user,
    passwd=db_passwords,
    port=3306
    )


# symbol行情数据基类
class BaseSymbolPrice(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    interval = CharField(column_name="interval", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    @classmethod
    def getSymbol(cls):
        pass

    class Meta:
        database = data_source_db
        legacy_table_names = False
        indexes = (
            (("symbol", "ts", "interval"), True),
        )


class XauUsd(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "XAUUSD"


class Dxy(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "DX-Y.NYB"


class DxyMt5(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "DXY_MT5"


class EurUsd(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "EURUSD"


class GbpUsd(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "GBPUSD"


class Tnx(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "^TNX"


class UsdCad(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "USDCAD"


class UsdChf(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "USDCHF"


class UsdJpy(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "USDJPY"


class UsdSek(BaseSymbolPrice):
    @classmethod
    def getSymbol(cls):
        return "USDSEK"


###############################################
# 组合价格数据存放在production_combined_data库中
production_combined_data_db = MySQLDatabase(
    'production_combined_data',
    host=db_host,
    user=db_user,
    passwd=db_passwords,
    port=3306
    )


###############################################
# 通用批量保存，保存对象以字典列表形式传入
def batch_save_by_model(symbol_model, dict_data_list, batch_size=500):
    while len(dict_data_list) > batch_size:
        batch = dict_data_list[:batch_size]
        with data_source_db.atomic():
            getattr(symbol_model, "replace_many")(batch).execute()
        dict_data_list = dict_data_list[batch_size:]
    else:
        with data_source_db.atomic():
            getattr(symbol_model, "replace_many")(dict_data_list).execute()


# 通用批量保存，保存对象以字典列表形式传入
def batch_save_by_symbol(symbol, dict_data_list, batch_size=500):
    valid = False
    for sc in BaseSymbolPrice.__subclasses__():
        if symbol == getattr(sc, "getSymbol")():
            valid = True
            batch_save_by_model(sc, dict_data_list, batch_size)
            break
    if not valid:
        raise Exception("symbol没有对应的Model:" + symbol)


# 根据symbol获取对应模型
def get_model_by_symbol(symbol):
    for sc in BaseSymbolPrice.__subclasses__():
        if symbol == getattr(sc, "getSymbol")():
            return sc


# 根据symbol获取对应的模型表名
def get_model_table_by_symbol(symbol):
    for sc in BaseSymbolPrice.__subclasses__():
        if symbol == getattr(sc, "getSymbol")():
            return sc._meta.table_name


# 通用单个保存，保存对象以字典形式传入
def save_by_model(symbol_model, dict_data):
    getattr(symbol_model, "replace")(**dict_data)


# 通用单个保存，保存对象以字典形式传入
def save_by_symbol(dict_data):
    valid = False
    symbol = dict_data['symbol']
    for sc in BaseSymbolPrice.__subclasses__():
        if symbol == getattr(sc, "getSymbol")():
            valid = True
            save_by_model(sc, dict_data)
            break
    if not valid:
        raise Exception("symbol没有对应的Model:" + symbol)
