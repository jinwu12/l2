from libs import fetcher
from apscheduler.schedulers.background import BackgroundScheduler
import time
import datetime
from libs import commons
from libs.database import *
import yfinance as yf
from decimal import Decimal
import pandas as pd


# 初始化后台调度器
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

# 专门for yfinance数据源的二次检查和补录


def check_yfinance_and_reupdate(interval, symbol='^TNX'):
    miss_logger = commons.create_logger('missing_ts')
    diff_logger = commons.create_logger('same_ts_diff_price')
    # 拉取接口的历史数据
    end = datetime.datetime.now() + datetime.timedelta(days=1)
    start = (datetime.datetime.now() - datetime.timedelta(days=6))
    o_data = yf.download(start=start, end=end,
                         interval=interval, tickers=symbol)
    # 逐行对比数据，记录差异
    df = pd.DataFrame(o_data)
    result_list = []
    # 获取symbol对应表名 
    tnx_tbl = get_model_table_by_symbol_value('^TNX')
    diff_count = 0
    # 遍历dataframe中的每一行
    for pd_timestamp, row in df.iterrows():
       # 将第一列时间转timestamp
       ts = int(pd_timestamp.to_pydatetime().timestamp())
       # 获取开盘价、最高价、最低价和调整后的收盘价;价格取小数点后4位
       open_price = Decimal(row['Open']).quantize(
           Decimal("0.0001"), rounding="ROUND_HALF_UP")
       high_price = Decimal(row['High']).quantize(
           Decimal("0.0001"), rounding="ROUND_HALF_UP")
       low_price = Decimal(row['Low']).quantize(
           Decimal("0.0001"), rounding="ROUND_HALF_UP")
       close_price = Decimal(row['Adj Close']).quantize(
           Decimal("0.0001"), rounding="ROUND_HALF_UP")
       # 逐条对比db中的数据,找出数据有差异的点
       sql = "select * from original_data_source." + tnx_tbl + " where `interval`='" + interval + "' and symbol_name ='" \
           + symbol + "' and ts = " + str(ts) + " and ( price_open != " + str(open_price) + " or price_high != " + str(high_price) + \
           " or price_low != " + str(low_price) + \
           " or price_closed != " + str(close_price) + ")"
       mycursor = data_source_db.execute_sql(sql)
       result = mycursor.fetchall()
       if len(result) > 0:
           diff_logger.error("数据不一致:%s", dict(symbol=symbol, interval=interval, ts=ts,
                                              price_open=open_price, price_high=high_price,
                                              price_low=low_price, price_closed=close_price))
    # 只要出现了不一致，就开始补录
    if diff_count > 0:
        weekly_date_reupdate(interval)

# 每周第一次补录函数


def weekly_date_reupdate(interval):
    end = datetime.datetime.now() + datetime.timedelta(days=1)
    start = (datetime.datetime.now() - datetime.timedelta(days=6))
    fetcher.fetch_data(start, end, interval)
    print(start, end)


# 添加数据检查任务，每工作日中午十一点及周日中午十一点进行，一旦发现数据有误则进行重录
# 小时级数据补录
scheduler.add_job(
    check_yfinance_and_reupdate,
    trigger='cron',
    day_of_week='mon-fri',
    hour='11',
    minute='01',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

scheduler.add_job(
    check_yfinance_and_reupdate,
    trigger='cron',
    day_of_week='sun',
    hour='11',
    minute='01',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)


# 分钟级数据补录
scheduler.add_job(
    check_yfinance_and_reupdate,
    trigger='cron',
    day_of_week='mon-fri',
    hour='12',
    minute='01',
    args=['1m'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

scheduler.add_job(
    check_yfinance_and_reupdate,
    trigger='cron',
    day_of_week='sun',
    hour='12',
    minute='01',
    args=['1m'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

# 添加调度器任务，每周六中午十二点执行数据补录
# 小时级数据补录
scheduler.add_job(
    weekly_date_reupdate,
    trigger='cron',
    day_of_week='sat',
    hour='11',
    minute='01',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)
# 分钟级数据补录
scheduler.add_job(
    weekly_date_reupdate,
    trigger='cron',
    day_of_week='sat',
    hour='13',
    args=['1m'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

# 启动调度器
scheduler.start()

while True:
    time.sleep(1)
