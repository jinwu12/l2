import datetime
import sys

sys.path.append("..")
from libs import commons, gen_combinations_price
import unittest


class TestFunctions(unittest.TestCase):

    def test_get_symbol_name_by_id(self):
        result = gen_combinations_price.get_symbol_name_by_id(1, [])
        self.assertEqual(0, len(result))

        data_list = [
            {'method_id': 1, 'symbol_name': 'XAUUSD', 'method_name': 'get_historical_data_from_mt5', 'timezone': 'EET',
             'symbol_value': 'XAUUSD', 'contract_size': None, 'digits': None, '3point_price': None},
            {'method_id': 2, 'symbol_name': 'TNX', 'method_name': 'get_historical_data_from_yfinance',
             'timezone': 'US/Eastern',
             'symbol_value': '^TNX', 'contract_size': None, 'digits': None, '3point_price': None},
            {'method_id': 3, 'symbol_name': 'DXY', 'method_name': 'get_historical_data_from_yfinance',
             'timezone': 'US/Eastern',
             'symbol_value': 'DX-Y.NYB', 'contract_size': None, 'digits': None, '3point_price': None},
            {'method_id': 4, 'symbol_name': 'EURUSD', 'method_name': 'get_historical_data_from_mt5', 'timezone': 'EET',
             'symbol_value': 'EURUSD', 'contract_size': None, 'digits': None, '3point_price': None}
        ]
        result = gen_combinations_price.get_symbol_name_by_id(1, data_list)
        self.assertEqual(1, len(result))
        self.assertEqual(1, result[0][0])
        self.assertEqual("XAUUSD", result[0][1])

        result = gen_combinations_price.get_symbol_name_by_id(-1, data_list)
        self.assertEqual(0, len(result))

    def test_get_lastest_price_before_dst_ts(self):
        test_db = commons.db_connect()
        dst_ts = 1640880000
        result = commons.get_lastest_price_before_dst_ts(test_db, "1h", "DXY", dst_ts)
        self.assertEqual("DX-Y.NYB", result[0])
        self.assertEqual(dst_ts, result[1])
        self.assertEqual(96.002, result[2])
        self.assertEqual(96.078, result[3])
        self.assertEqual(95.993, result[4])
        self.assertEqual(96.069, result[5])

        result = commons.get_lastest_price_before_dst_ts(test_db, "1h", "DXY", 0)
        self.assertTrue(result is None)


    def test_get_historical_symbol_rates_list(self):
        test_db = commons.db_connect()
        data = gen_combinations_price.get_historical_symbol_rates_list(test_db, '2021-12-04', '2022-01-15', '1h')
        self.assertTrue(len(data) > 0)
        for item in data:
            ts = -1
            for sub_item in item:   # 同list中的数据ts应该一致
                cur_ts = sub_item.get('value')[1]
                if ts < 0:
                    ts = cur_ts
                else:
                    self.assertEqual(ts, cur_ts)


    def test_cal_comb_price_strict_match(self):
        test_db = commons.db_connect()
        data = gen_combinations_price.get_historical_symbol_rates_list(test_db, '2022-02-12 03:00:00',
                                                                       '2022-02-12 04:59:59', '1h')
        result = gen_combinations_price.cal_comb_price_strict_match(data, 1, test_db)
        print(result)


if __name__ == '__main__':
    unittest.main()
