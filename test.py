from re import I
from libs import fetcher
import time
import datetime
from libs import commons
import yfinance as yf
from decimal import Decimal
import pandas as pd



miss_logger = commons.create_logger('missing_ts')
diff_logger = commons.create_logger('same_ts_diff_price')

symbol = '^TNX'
interval = '1h'
# 拉取接口的历史数据
end = datetime.datetime.now() + datetime.timedelta(days=1)
start = (datetime.datetime.now() - datetime.timedelta(days=729))
o_data = yf.download(start=start, end=end, interval=interval, tickers=symbol)

# 修改dataframe中的时间为时间戳并返回结果列表
df = pd.DataFrame(o_data)
result_list = []
db = commons.db_connect()
mycursor = db.cursor()
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
    sql = "select * from original_data_source.tnx where `interval`='" + interval + "' and symbol_name ='" \
        + symbol + "' and ts = " + str(ts) + " and ( price_open != " + str(open_price) + " or price_high != " + str(high_price) + \
        " or price_low != " + str(low_price) + \
        " or price_closed != " + str(close_price) + ")"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if len(result) > 0:
        diff_logger.error("数据不一致:%s", dict(symbol=symbol, interval=interval, ts=ts,
                                           price_open=open_price, price_high=high_price,
                                           price_low=low_price, price_closed=close_price))
