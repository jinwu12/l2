import logging

import mysql.connector
from configparser import ConfigParser
import datetime


LOG_FORMAT = '%(asctime)s - %(name)s[%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
# logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
log_map = {}



# 创建日志对象
def create_logger(name='app'):
    logger = log_map.get(name)
    if logger is None:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        log_map[name] = logger
        # 输出到日志文件
        handler = logging.FileHandler(name+".txt")
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

        # 将日志也输出到控制台上
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(LOG_FORMAT))
        console.setLevel(logging.DEBUG)
        logger.addHandler(console)

    return logger

#根据symbol name获取对应的symbol values
def get_symbol_value(symbol_name, db):
    symbol_method_db = db
    symbol_method_db_cursor = symbol_method_db.cursor()
    #获取symbol name对应的symbol value，如果有多个则只返回第一个
    get_first_symbol_value = 'select symbol_value from Global_Config.Tbl_symbol_method where symbol_name=\''+symbol_name+'\''
    symbol_method_db_cursor.execute(get_first_symbol_value)
    return symbol_method_db_cursor.fetchall()[0][0]


#根据配置文件中的db配置，连接数据库
def db_connect():
    #读取配置文件中的数据配置
    cfg = ConfigParser()
    cfg.read('./config.ini')
    db_host = cfg.get('database','host')
    db_user = cfg.get('database','user')
    db_passwords = cfg.get('database','passwords')
    
    #连接数据库
    mydb = mysql.connector.connect(
            host = db_host,
            user = db_user,
            passwd = db_passwords
            )
    return mydb

#根据各symbol method拉取数据的格式，入库到对应的表中
def insert_historical_original_data_to_db(symbol_name,data_list,interval,db):
    source_data_db = db
    source_data_cursor = source_data_db.cursor()
    #根据symbol_name及interval生成table name,按月分表
    year = datetime.datetime.utcnow().year
    month = datetime.datetime.utcnow().strftime("%m")
    table_name = 'original_data_source.'+symbol_name+'_'+interval+'_original_data_'+str(year)+str(month)
    print(table_name)
    #建立对应数据表
    create_table_sql = 'create table IF NOT EXISTS '+table_name+'  like original_data_source.single_symbol_original_data_template'
    source_data_cursor.execute(create_table_sql)

    #生成模版sql
    insert_source_data_template_sql = 'insert into '+table_name+'(symbol_name,ts,price_open,price_high,price_low,price_closed) values(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE price_open=VALUES(price_open), price_high=VALUES(price_high), price_low=VALUES(price_low), price_closed=VALUES(price_closed)'

    #通过executemany来批量执行语句
    n=source_data_cursor.executemany(insert_source_data_template_sql,data_list)
    db.commit()


# 拉取Tbl_symbol_method全量的属性
def get_all_symbol_attr(db):
    cursor = db.cursor(dictionary=True)
    sql = 'select method_id, symbol_name, method_name, timezone, \
        symbol_value, contract_size, digits, 3point_price from Global_Config.Tbl_symbol_method'
    cursor.execute(sql)
    return cursor.fetchall()

# 从db中拉取特定symbol到指定时间戳之前的最新报价
def get_lastest_price_before_dst_ts(db, interval, symbol, dst_ts):
    year_month_suffix = datetime.datetime.utcfromtimestamp(datetime.datetime.utcnow().timestamp()).strftime("%Y%m")
    tbl = str.format("{}_{}_original_data_{}", symbol, interval, year_month_suffix)
    sql = "select symbol_name, ts, price_open, price_high, price_low, price_closed from original_data_source.%s where ts<=%d order by ts desc limit 1" % (tbl, dst_ts)
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result


