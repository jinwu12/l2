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
config_db = MySQLDatabase('Global_Config', host=db_host, user=db_user, passwd=db_passwords, port=3306)


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
    _3point_price = DecimalField(column_name="3point_price", max_digits=10)

    class Meta:
        database = config_db
        table_name = "Tbl_symbol_method"


###############################################
data_source_db = MySQLDatabase('original_data_source', host=db_host, user=db_user, passwd=db_passwords, port=3306)


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
    def getSymbol(self):
        pass

    class Meta:
        database = data_source_db
        legacy_table_names = False


class XauUsd(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "XAUUSD"


class Dxy(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "DXY"


class DxyMt5(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "DXY_MT5"


class EurUsd(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "EURUSD"


class GbpUsd(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "GBPUSD"


class Tnx(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "TNX"


class UsdCad(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "USDCAD"


class UsdChf(BaseSymbolPrice):
    def getSymbol(self):
        return "USDCHF"


class UsdJpy(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "USDJPY"


class UsdSek(BaseSymbolPrice):
    @classmethod
    def getSymbol(self):
        return "USDSEK"


###############################################
# 通用批量保存
def batch_save_by_model(symbol_model, dict_data_list, batch_size=500):
    while len(dict_data_list) > batch_size:
        batch = dict_data_list[:batch_size]
        with data_source_db.atomic():
            getattr(symbol_model, "insert_many")(batch).execute()
        dict_data_list = dict_data_list[batch_size:]
    else:
        with data_source_db.atomic():
            getattr(symbol_model, "insert_many")(dict_data_list).execute()


# 通用批量保存
def batch_save_by_symbol(symbol, dict_data_list, batch_size=500):
    valid = False
    for sc in BaseSymbolPrice.__subclasses__():
        if symbol == getattr(sc, "getSymbol")():
            valid = True
            batch_save_by_model(sc, dict_data_list, batch_size)
            break
    if not valid:
        raise Exception("symbol没有对应的Model:" + symbol)


# 通用单个保存
def save_by_model(symbol_model, dict_data):
    getattr(symbol_model, "create")(**dict_data)


# 通用单个保存
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
