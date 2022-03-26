import ssl
import unittest
from datetime import datetime
import time

import pytz
import yfinance as yf
from dateutil.relativedelta import relativedelta

from libs import fetcher
from libs.database import *


class MyTestCase(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls) -> None:
    #     print("drop tables...")
    #     data_source_db.drop_tables([XauUsd, Dxy, DxyMt5, EurUsd, GbpUsd, Tnx, UsdCad, UsdChf, UsdJpy, UsdSek])
    #     print("create tables...")
    #     data_source_db.create_tables([XauUsd, Dxy, DxyMt5, EurUsd, GbpUsd, Tnx, UsdCad, UsdChf, UsdJpy, UsdSek])

    def test_copy_rates_range(self):
        import MetaTrader5 as mt5
        account = AccountInfo.get(1)
        if not mt5.initialize(
                login=int(account.name),
                password=account.password,
                server=account.server
        ):
            self.fail("login failed!")

        # m5的结论是，传入的日期时间要带时区，平台将转换为UTC时间作处理。
        # 当传入的时间参数不带时区时，默认为客户端当前时区

        # 做个测试，以不同时区的时间参数去获取数据，结果应该一致
        # UTC 2022-3-15 0:0:0 ~ 2022-3-16 0:0:0
        symbol = "EURUSD"
        start = datetime(2022, 3, 15, 0, 0, 0, tzinfo=pytz.timezone('UTC'))
        end = datetime(2022, 3, 16, 0, 0, 0, tzinfo=pytz.timezone('UTC'))
        utc_data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
        print(utc_data)
        print(len(utc_data))
        # 时间区间范围是闭区间，一分钟一条数据，应该有1441条，实际是1440条(怪异)，小时级数据15号0点到16号0点是25条
        self.assertEqual(60 * 24, len(utc_data))
        self.assertEqual(int(start.timestamp()), utc_data[0][0])  # 校验第一条数据：应该与开始时间一致
        self.assertEqual(int(end.timestamp()), utc_data[-1][0])  # 校验最后一条数据：应该与结束时间一致

        # UTC+8 2022-3-15 8:0:0 ~ 2022-3-16 8:0:0 与上面的UTC时间一致
        start = datetime(2022, 3, 15, 8, 0, 0, tzinfo=pytz.timezone('ETC/GMT-8'))  # 不能传LMT时区！！！
        end = datetime(2022, 3, 16, 8, 0, 0, tzinfo=pytz.timezone('ETC/GMT-8'))
        gmt_m_8_data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
        print(gmt_m_8_data)
        print(len(gmt_m_8_data))
        self.assertEqual(60 * 24, len(gmt_m_8_data))
        self.assertEqual(int(start.timestamp()), gmt_m_8_data[0][0])  # 校验第一条数据：应该与开始时间一致
        self.assertEqual(int(end.timestamp()), gmt_m_8_data[-1][0])  # 校验最后一条数据：应该与结束时间一致
        # 与utc时间获取的数据应该是一致的
        self.assertEqual(utc_data.tolist(), gmt_m_8_data.tolist())

        # 下面是获取小时数据的情况
        start = datetime(2022, 3, 15, 0, 0, 0, tzinfo=pytz.timezone('UTC'))
        end = datetime(2022, 3, 17, 0, 0, 0, tzinfo=pytz.timezone('UTC'))
        data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)
        print(data)
        print(25, len(data))

    def test_get_historical_data_from_yfinance(self):
        now = datetime.now()
        symbol = '^TNX'
        interval = '1m'
        data = fetcher.get_historical_data_from_yfinance(symbol, interval, now - relativedelta(days=7), now,
                                                         'ETC/GMT-8')
        # 存档进数据库
        # from libs.database import Tnx
        # Tnx.insert_many(data).execute()
        self.assertEqual(len(data) > 0, True)
        record = data[0]
        print(record)
        self.assertEqual(symbol, record['symbol'])
        self.assertEqual(interval, record['interval'])

    def test_get_historical_data_from_mt5(self):
        symbol = "XAUUSD"
        interval = "1h"
        start = datetime.now() - relativedelta(days=3)
        end = datetime.now()
        data_list = fetcher.get_historical_data_from_mt5(symbol, interval, start, end)
        print(data_list)

    def test_fetch_data(self):
        interval = "1h"
        # start = datetime.now() - relativedelta(days=3)
        # end = datetime.now()
        start = datetime.strptime('2022-01-01 0:0:0', '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime('2022-01-03 0:0:0', '%Y-%m-%d %H:%M:%S')
        fetcher.fetch_data(start, end, interval)


if __name__ == '__main__':
    unittest.main()
