import datetime
import os.path
import sys
from configparser import ConfigParser
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

import mysql

from libs import commons

sys.path.append("..")
from libs.database import *

logger = commons.create_logger()


# 检验行情记录数据是否完整
def verify_records(db, table, category='1h'):
    # 表所在月的天数
    first_day_of_the_month = datetime.strptime(table[str.rindex(table, "_") + 1:] + "01", "%Y%m%d")
    days_of_the_month = (first_day_of_the_month + relativedelta(months=1) - first_day_of_the_month).days
    if first_day_of_the_month.month == datetime.now().month:  # 当月
        days_of_the_month = (datetime.now() - first_day_of_the_month).days
    # 根据类型和月份来计算理论的记录数
    record_count_in_theory = 24 * days_of_the_month
    if category == '1m':
        record_count_in_theory = 60 * 24 * days_of_the_month
    cursor = db.cursor()
    cursor.execute("select count(1) from %s" % table)
    record_count = cursor.fetchone()[0]
    if record_count_in_theory != record_count:
        logger.error("%s表数据量校验不通过: 应有%d条，实有%d条", table, record_count_in_theory, record_count)
        return False
    return False


def make_transfer():
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwords,
        database='original_data_source'
    )

    # 创建表
    data_source_db.create_tables([XauUsd, Dxy, DxyMt5, EurUsd, GbpUsd, Tnx, UsdCad, UsdChf, UsdJpy, UsdSek])

    cursor = db.cursor()
    sql = 'show tables'
    cursor.execute(sql)
    tables = cursor.fetchall()
    for table in tables:
        tbl = table[0]
        if ("_1h" in tbl or "_1m" in tbl) and len(tbl[str.rindex(tbl, "_") + 1:]) == 6:  # 不处理表名不合法的
            # 数据校验
            # if not verify_records(db, tbl, '1h' if "_1h" in tbl else "1m"):
                # print("表数据校验失败：", tbl)
                # continue
            # 数据迁移
            data_cursor = db.cursor(dictionary=True)
            data_cursor.execute("select * from %s" % tbl)
            batch = []
            logger.info("开始转移表: %s", tbl)
            transfer_count = 0
            for record in data_cursor.fetchall():
                # print(record)
                batch.append(dict(symbol='XAUUSD', category='1h' if "_1h" in tbl else "1m", ts=record['ts'],
                                  price_open=record['price_open'], price_high=record['price_high'],
                                  price_low=record['price_low'], price_closed=record['price_closed']))
                if len(batch) >= 500:
                    with data_source_db.atomic():
                        XauUsd.insert_many(batch).execute()
                    transfer_count += len(batch)
                    batch.clear()
            if len(batch) > 0:
                with data_source_db.atomic():
                    XauUsd.insert_many(batch).execute()
                transfer_count += len(batch)
                batch.clear()
            logger.info("表%s数据转移完成，共迁移%d条数据", tbl, transfer_count)


if __name__ == '__main__':
    make_transfer()
