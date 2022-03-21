import logging
import logging.config

import mysql.connector
from configparser import ConfigParser
from datetime import datetime

import pytz

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
        # 输出到日志文件,按天分文件，保存30天
        handler = logging.handlers.TimedRotatingFileHandler('logs/'+name+'_today.log', 'D', 1 , 30)
        handler.suffix = "%Y-%m-%d.log"
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

        # 将日志也输出到控制台上
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(LOG_FORMAT))
        console.setLevel(logging.DEBUG)
        logger.addHandler(console)

    return logger


# 将指定时区的时间文本转化为utc时区的unix时间戳，以便存入db：2022-02-16 09:36:00, "US/Eastern"
def datetime_to_timestamp(datetime_str, timezone):
    return int(pytz.timezone(timezone).localize(datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')).timestamp())


# 将时间戳转换为时间文本，以便展示或查看
def timestamp_to_datetime_str(timestamp, timezone, format='%Y-%m-%d %H:%M:%S%z'):
    return datetime.fromtimestamp(timestamp, pytz.timezone(timezone)).strftime(format)


# 将带时区的日期时间文本转换为时间戳: 2022-02-16 09:36:00-05:00 -> 1645022160
def datetime_str_with_timezone_to_timestamp(time):
    return datetime.strptime(time, '%Y-%m-%d %H:%M:%S%z').timestamp()



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


# 从db中拉取特定symbol到指定时间戳之前的最新报价
def get_lastest_price_before_dst_ts(db, interval, symbol, dst_ts):
    year_month_suffix = datetime.utcfromtimestamp(datetime.utcnow().timestamp()).strftime("%Y%m")
    tbl = str.format("{}_{}_original_data_{}", symbol, interval, year_month_suffix)
    sql = "select symbol_name, ts, price_open, price_high, price_low, price_closed from original_data_source.%s where ts<=%d order by ts desc limit 1" % (tbl, dst_ts)
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result


