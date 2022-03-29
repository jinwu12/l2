import unittest

import sys

sys.path.append("..")
from libs.database import *


class DatabaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 创建表
        print("create tables...")
        data_source_db.create_tables([XauUsd, Dxy, DxyMt5, EurUsd, GbpUsd, Tnx, UsdCad, UsdChf, UsdJpy, UsdSek,
                                      CombinedSymbol])

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
        self.assertEqual(3.000000, symbol.trio_point_price)

    def test_xauusd(self):
        item = XauUsd(symbol='XAUUSD', ts=1640970000, interval='1h',
                      price_open=1822.42, price_high=1824.29, price_low=1820.38,
                      price_closed=1822)
        item.save()

    def test_dynamic_save(self):
        count = XauUsd.select().count()
        item = dict(symbol='XAUUSD', ts=1640970000, interval='1h', price_open=999.99, price_high=1824.29,
                    price_low=1820.38, price_closed=1822)
        items = [item, item, item]

        batch_save_by_model(XauUsd, items, batch_size=2)
        self.assertEqual(len(items) + count, XauUsd.select().count())

        count = XauUsd.select().count()
        batch_save_by_symbol('XAUUSD', items, batch_size=2)
        self.assertEqual(len(items) + count, XauUsd.select().count())

        count = XauUsd.select().count()
        save_by_model(XauUsd, item)
        self.assertEqual(1 + count, XauUsd.select().count())

        count = XauUsd.select().count()
        save_by_symbol(item)
        self.assertEqual(1 + count, XauUsd.select().count())

    def test_custom_query(self):
        cursor = data_source_db.execute_sql('select * from xau_usd where ts>%s', 10000)
        print(len(cursor.fetchall()))

    def test_cache(self):
        print(global_cache.get_symbol_by_id(1).name)
        print(global_cache.get_symbol_by_id(2).name)
        print(global_cache.get_symbol_by_id(22))

if __name__ == '__main__':
    unittest.main()
