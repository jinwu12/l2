import ssl
import unittest
from datetime import datetime, timedelta

import pytz
import yfinance as yf

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
        end = datetime(2022, 3, 16, 0, 0, 0, tzinfo=pytz.timezone('UTC'))
        data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)
        print(data)
        self.assertEqual(25, len(data))

    def test_yfinance_download(self):
        # yfinance的download方法中的start和end参数支持str(精确到天)和datetime两种形式，
        # 到实现层时，将以当前时区(忽略datetime中的时区)转换为时间戳去获取具体的数据，
        # 而返回的数据带时间偏移，比如2022-03-24 10:12:00-04:00
        try:
            start = datetime(2022, 3, 24, 22, 12, 0, tzinfo=pytz.timezone('ETC/GMT-8'))
            end = datetime(2022, 3, 24, 22, 13, 0, tzinfo=pytz.timezone('ETC/GMT-8'))
            # 时间区间是前闭后开，比较奇怪的是返回了一个23:59的数据，先去掉
            data = yf.download(tickers='^TNX', interval='1m', start=start, end=end, progress=False)
            data = data[:-1]  # 去掉23:59:00这条数据
            print(data)
            self.assertEqual(1, len(data))
            self.assertEqual(1, len(data.index.tolist()))
            # 返回的数据timestamp与start对应一致
            self.assertEqual(start.timestamp(), data.index.tolist()[0].to_pydatetime().timestamp())
            ts = start.timestamp()

            start = datetime(2022, 3, 24, 22, 12, 0, tzinfo=pytz.timezone('ETC/UTC'))
            end = datetime(2022, 3, 24, 22, 13, 0, tzinfo=pytz.timezone('ETC/UTC'))
            utc_data = yf.download(tickers='^TNX', interval='1m', start=start, end=end, progress=False)
            utc_data = utc_data[:-1]  # 去掉23:59:00这条数据
            print(utc_data)
            self.assertEqual(1, len(utc_data))
            self.assertEqual(1, len(utc_data.index.tolist()))
            # 返回的数据timestamp与start不一致！
            self.assertNotEqual(start.timestamp(), utc_data.index.tolist()[0].to_pydatetime().timestamp())
            # 返回的数据timestamp与start时间的字面时间转本地时区对应的时间戳一致！=》说明传入的时间参数的时区被忽略了，以当前时区为准了
            self.assertEqual(ts, utc_data.index.tolist()[0].to_pydatetime().timestamp())
            # 数据其实是一致的
            self.assertEqual(data.values.tolist(), utc_data.values.tolist())

            # 再试试其他时区
            start = datetime(2022, 3, 24, 22, 12, 0, tzinfo=pytz.timezone('ETC/GMT+3'))
            end = datetime(2022, 3, 24, 22, 13, 0, tzinfo=pytz.timezone('ETC/GMT+3'))
            # 时间区间是前闭后开，比较奇怪的是返回了一个23:59的数据，先去掉
            data2 = yf.download(tickers='^TNX', interval='1m', start=start, end=end, progress=False)
            data2 = data2[:-1]  # 去掉23:59:00这条数据
            print(data2)
            self.assertEqual(1, len(data2))
            self.assertEqual(1, len(data2.index.tolist()))
            # 返回的数据timestamp与start不一致！
            self.assertNotEqual(start.timestamp(), data2.index.tolist()[0].to_pydatetime().timestamp())
            # 返回的数据timestamp与start时间的字面时间转本地时区对应的时间戳一致！=》说明传入的时间参数的时区被忽略了，以当前时区为准了
            self.assertEqual(ts, data2.index.tolist()[0].to_pydatetime().timestamp())
            # 数据其实是一致的
            self.assertEqual(data.values.tolist(), data2.values.tolist())
            self.assertEqual(utc_data.values.tolist(), data2.values.tolist())
        except (ssl.SSLEOFError, ssl.SSLError):
            self.fail("error....")

    def test_get_historical_data_from_yfinance(self):
        # 天级数据
        symbol = '^TNX'
        interval = '1d'
        start = datetime(2022, 1, 3)
        end = datetime(2022, 1, 7)
        data = fetcher.get_historical_data_from_yfinance(symbol, interval, start, end)
        self.assertEqual(4, len(data))
        records = [{'symbol': symbol, 'interval': interval, 'ts': int(start.timestamp()),
                    'price_open': '1.5340',
                    'price_high': '1.6350', 'price_low': '1.5330',
                    'price_closed': '1.6280'},
                   {'symbol': symbol, 'interval': interval, 'ts': int((start + timedelta(days=1)).timestamp()),
                    'price_open': '1.6630',
                    'price_high': '1.6860', 'price_low': '1.6540',
                    'price_closed': '1.6680'},
                   {'symbol': symbol, 'interval': interval, 'ts': int((start + timedelta(days=2)).timestamp()),
                    'price_open': '1.6600',
                    'price_high': '1.7100', 'price_low': '1.6470',
                    'price_closed': '1.7050'},
                   {'symbol': symbol, 'interval': interval, 'ts': int((start + timedelta(days=3)).timestamp()),
                    'price_open': '1.7330',
                    'price_high': '1.7440', 'price_low': '1.7210',
                    'price_closed': '1.7330'},
                   ]
        self.assertEqual(records, data)
        # 小时级数据
        symbol = '^TNX'
        interval = '1h'
        start = datetime(2022, 1, 5, tzinfo=pytz.timezone('ETC/GMT+4'))
        end = datetime(2022, 1, 6, tzinfo=pytz.timezone('ETC/GMT+4'))
        data = fetcher.get_historical_data_from_yfinance(symbol, interval, start, end)
        print(data)
        self.assertEqual(8, len(data))  # 7条，加一条奇怪的数据...
        print('------------')
        print("入参：start=" + start.strftime('%Y-%m-%d %H:%M:%S%z'), ", end=" + end.strftime('%Y-%m-%d %H:%M:%S%z'))
        for item in data:
            print(commons.timestamp_to_datetime_str(item['ts'], 'ETC/GMT+4'), item)

    def test_get_historical_data_from_mt5(self):
        symbol = "XAUUSD"
        interval = "1h"
        start = datetime(2022, 3, 24, 18, 00, 0, tzinfo=pytz.timezone('ETC/UTC'))
        end = datetime(2022, 3, 24, 22, 00, 0, tzinfo=pytz.timezone('ETC/UTC'))
        data_list = fetcher.get_historical_data_from_mt5(symbol, interval, start, end)
        for item in data_list:
            print(item)
        self.assertEqual(5, len(data_list))
        self.assertEqual({'symbol': 'XAUUSD', 'interval': '1h', 'ts': 1648144800, 'price_open': 1964.86,
                          'price_high': 1965.54, 'price_low': 1958.51, 'price_closed': 1963.0}, data_list[0])

    def test_fetch_data(self):
        interval = "1h"
        # start = datetime.now() - relativedelta(days=3)
        # end = datetime.now()
        start = datetime.strptime('2022-01-03 0:0:0', '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime('2022-01-05 0:0:0', '%Y-%m-%d %H:%M:%S')
        fetcher.fetch_data(start, end, interval)


if __name__ == '__main__':
    unittest.main()
