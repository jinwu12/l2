import datetime
import sys

sys.path.append("..")
from libs import commons, gen_combinations_price
from libs.database import *
import unittest


class TestFunctions(unittest.TestCase):

    def test_get_lastest_price_before_dst_ts(self):
        test_db = commons.db_connect()
        dst_ts = 1641160800
        result = gen_combinations_price.get_lastest_price_before_dst_ts(test_db, "1h", "DX-Y.NYB", dst_ts)
        self.assertEqual("DX-Y.NYB", result[0])
        self.assertEqual(dst_ts, result[1])
        self.assertEqual(95.67, result[2])
        self.assertEqual(95.67, result[3])
        self.assertEqual(95.67, result[4])
        self.assertEqual(95.67, result[5])

        result = gen_combinations_price.get_lastest_price_before_dst_ts(test_db, "1h", "DX-Y.NYB", 0)
        self.assertTrue(result is None)

    def test_get_historical_symbol_rates_list(self):
        start = datetime.datetime.strptime('2021-12-04', '%Y-%m-%d')
        end = datetime.datetime.strptime('2022-01-15', '%Y-%m-%d')
        data = gen_combinations_price.get_historical_symbol_rates_list(start, end, '1h')
        print(data)
        self.assertTrue(len(data) > 0)
        for item in data:
            ts = -1
            for sub_item in item:  # 同list中的数据ts应该一致
                cur_ts = sub_item.get('value')[1]
                if ts < 0:
                    ts = cur_ts
                else:
                    self.assertEqual(ts, cur_ts)

    def test_calculate_combination_3point_price(self):
        combination = Combination(id=1, symbol_list="1,10", combination_3point_price=6)
        self.assertEqual(6, gen_combinations_price.calculate_combination_3point_price(combination))
        combination = Combination(id=1, symbol_list="1,10")
        self.assertEqual(6, gen_combinations_price.calculate_combination_3point_price(combination))

    def test_cal_comb_price_strict_match(self):
        start = datetime.datetime.strptime('2022-02-12 03:00:00', '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime('2022-02-12 04:59:59', '%Y-%m-%d %H:%M:%S')
        data = gen_combinations_price.get_historical_symbol_rates_list(start, end, '1h')
        result = gen_combinations_price.cal_comb_price_strict_match(data, 1)
        print(result)


    def test_check_combinations(self):
        gen_combinations_price.check_combinations()


if __name__ == '__main__':
    unittest.main()
