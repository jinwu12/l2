import unittest
from datetime import datetime
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

    def test_get_historical_data_from_yfinance(self):
        now = datetime.now()
        symbol = '^TNX'
        interval = '1m'
        data = fetcher.get_historical_data_from_yfinance(symbol, interval, now - relativedelta(days=7), now, 'US/Eastern')
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
        interval = "1m"
        # start = datetime.now() - relativedelta(days=3)
        # end = datetime.now()
        start = datetime.strptime('2022-01-01 0:0:0', '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime('2022-02-1 0:0:0', '%Y-%m-%d %H:%M:%S')
        fetcher.fetch_data(start, end, interval)


if __name__ == '__main__':
    unittest.main()
