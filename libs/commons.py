import logging
import logging.config

from datetime import datetime
import os

import pytz

LOG_FORMAT = '%(asctime)s - %(name)s[%(filename)s:%(lineno)d] [%(threadName)s] - %(levelname)s - %(message)s'
# logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
log_map = {}


def create_logger(name='app'):
    """
    创建日志对象
    :param name: 日志名，对应保存为logs/<name>.txt
    :return: 日志对象
    """
    logger = log_map.get(name)
    if logger is None:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        log_map[name] = logger
        # 输出到日志文件,按天分文件，保存30天
        handler = logging.handlers.TimedRotatingFileHandler('logs/' + name + '.' + str(os.getpid()) + '.log', 'D', 1, 30)
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


def datetime_to_timestamp(datetime_str, timezone):
    """将指定时区的时间文本转化为utc时区的unix时间戳，以便存入db：2022-02-16 09:36:00, "ETC/GMT-3" """
    return int(pytz.timezone(timezone).localize(datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')).timestamp())


def timestamp_to_datetime_str(timestamp, timezone="UTC", format='%Y-%m-%d %H:%M:%S%z'):
    """将时间戳转换为时间文本，以便展示或查看"""
    return datetime.fromtimestamp(timestamp, pytz.timezone(timezone)).strftime(format)


def datetime_str_with_timezone_to_timestamp(time):
    """将带时区的日期时间文本转换为时间戳: 2022-02-16 09:36:00-05:00 -> 1645022160"""
    return datetime.strptime(time, '%Y-%m-%d %H:%M:%S%z').timestamp()


def check_and_fix_timestamp(timestamp, interval='1m'):
    """检查并修正时间戳(比如，interval是1分钟，然后时间戳却不是整分)，向下取整"""
    return timestamp - timestamp % dict({'1m': 60, '1h': 60 * 60})[interval]


def get_timezone_timestamp_offset(timezone):
    """获取指定时区相对于UTC时间的时间戳偏移值(单位为秒)"""
    return datetime.now(pytz.timezone(timezone)).utcoffset().total_seconds()
