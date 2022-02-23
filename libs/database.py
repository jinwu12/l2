from configparser import ConfigParser

from peewee import *
import mysql.connector

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


class XauUsd(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "xau_usd"


class Dxy(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "dxy"


class DxyMt5(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "dxy_mt5"


class EurUsd(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "eur_usd"


class GbpUsd(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "gbp_usd"


class Tnx(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "tnx"


class UsdCad(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "usd_cad"


class UsdChf(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "usd_chf"


class UsdJpy(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "usd_jpy"


class UsdSek(Model):
    id = AutoField(column_name="id", primary_key=True)
    symbol = CharField(column_name="symbol_name", max_length=256)
    ts = TimestampField(index=True)
    category = CharField(column_name="category", max_length=4, index=True)
    price_open = DoubleField()
    price_high = DoubleField()
    price_low = DoubleField()
    price_closed = DoubleField()
    comments = TextField()

    class Meta:
        database = data_source_db
        table_name = "usd_sek"


# 创建表
data_source_db.create_tables([XauUsd, Dxy, DxyMt5, EurUsd, GbpUsd, Tnx, UsdCad, UsdChf, UsdJpy, UsdSek])
