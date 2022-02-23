import unittest

import sys

sys.path.append("..")
from libs.database import *


class DatabaseTestCase(unittest.TestCase):
    def test_account_query(self):
        accounts = AccountInfo.select()
        self.assertEqual(1, len(accounts))
        account = accounts[0]
        self.assertEqual(1, account.id)
        self.assertEqual("5348288", account.name)
        self.assertEqual("mt5", account.platform)
        self.assertEqual("ICMarketsSC-MT5", account.server)
        self.assertEqual("Hw5nFCew", account.password)
        self.assertEqual("获取正式环境数据账号", account.description)

    def test_symbol_query(self):
        symbols = Symbol.select()
        self.assertEqual(10, len(symbols))
        symbol = symbols[0]
        self.assertEqual(1, symbol.id)
        self.assertEqual("XAUUSD", symbol.name)
        self.assertEqual("get_historical_data_from_mt5", symbol.method)
        self.assertEqual("Turkey为夏令时时区（GMT+3），EET为冬令时时区（GMT+2）", symbol.comments)
        self.assertEqual("EET", symbol.timezone)
        self.assertEqual("XAUUSD", symbol.symbol_value)
        self.assertIsNone(symbol.contract_size)
        self.assertIsNone(symbol.digits)
        self.assertEqual(3.000000, symbol._3point_price)

    def test_xauusd(self):
        item = XauUsd(symbol='XAUUSD', ts=1640970000, category='1h',
                      price_open=1822.42, price_high=1824.29, price_low=1820.38,
                      price_closed=1822)
        item.save()


if __name__ == '__main__':
    unittest.main()
