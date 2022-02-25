import unittest
from datetime import datetime
from dateutil.relativedelta import relativedelta

from libs import fetcher


class MyTestCase(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
