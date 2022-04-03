import datetime
import json
import sys
from unittest.mock import Mock, patch
from playhouse.shortcuts import model_to_dict

sys.path.append("..")
from libs import gen_combinations_price
from libs.database import *
import unittest


class TestFunctions(unittest.TestCase):

    def test_get_lastest_price_before_dst_ts(self):
        dst_ts = 1641160800
        result = gen_combinations_price.get_lastest_price_before_dst_ts("DX-Y.NYB", "1h", dst_ts)
        print(result)
        self.assertEqual("DX-Y.NYB", result['symbol'])
        self.assertEqual(dst_ts, result['ts'])
        self.assertEqual(95.67, result['price_open'])
        self.assertEqual(95.67, result['price_high'])
        self.assertEqual(95.67, result['price_low'])
        self.assertEqual(95.67, result['price_closed'])

        result = gen_combinations_price.get_lastest_price_before_dst_ts("DX-Y.NYB", "1h", 0)
        self.assertTrue(result is None)

    def test_get_historical_symbol_rates_list(self):
        start = 1638547200
        end = 1639065600
        data = gen_combinations_price.get_historical_symbol_rates_list([1, 4], start, end, '1h')
        print(len(data))
        for item in data:
            print(item)
        self.assertTrue(len(data) > 0)
        for item in data:
            ts = -1
            for sub_item in item:  # 同list中的数据ts应该一致
                cur_ts = sub_item['ts']
                if ts < 0:
                    ts = cur_ts
                else:
                    self.assertEqual(ts, cur_ts)

    def test_calculate_combination_3point_price(self):
        combination = Combination(id=1, symbol_list="1,10", combination_3point_price=6)
        self.assertEqual(6, gen_combinations_price.calculate_combination_3point_price(combination))
        combination = Combination(id=1, symbol_list="1,10")
        self.assertEqual(6, gen_combinations_price.calculate_combination_3point_price(combination))

    def test_check_combinations(self):
        gen_combinations_price.check_combinations()

    def test_calc_combo_price_strict_match(self):
        rate1 = {'symbol': 'XAUUSD', 'interval': '1h', 'ts': 1641394800, 'price_open': 1.6490, 'price_high': 1.6580,
                 'price_low': 1.6470, 'price_closed': 1.6530}
        rate2 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641394800, 'price_open': 2.250, 'price_high': 2.580,
                 'price_low': 2.490, 'price_closed': 2.560}
        ##### mock #########
        # 指定XAUUSD和EURUSD的3点价
        rate1_trio_price = 4.2
        rate2_trio_price = 5
        values = {1: Symbol(id=1, name='XAUUSD', symbol_value='XAUUSD', trio_point_price=rate1_trio_price),
                  4: Symbol(id=4, name='EURUSD', symbol_value='EURUSD', trio_point_price=rate2_trio_price)}
        mock_get_symbol_by_id = Mock(side_effect=lambda x: values.get(x))
        with patch('libs.database.Cache.get_symbol_by_id', mock_get_symbol_by_id):
            ############ strict_match #############
            # 正常计算
            symbol_rates_list = [rate1, rate2]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            mode = 'strict_match'
            data = gen_combinations_price.calc_combo_price_strict_match(symbol_rates_list, combination)
            self.assertIsNotNone(data)
            self.assertTrue(mode in data['symbol'])
            print(data)
            # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
            self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3,
                             data['price_open'])
            self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3,
                             data['price_high'])
            self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3,
                             data['price_low'])
            self.assertEqual(
                rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] / rate2_trio_price * 3,
                data['price_closed'])

            # 给的rates数据缺一个
            symbol_rates_list = [rate1]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_strict_match(symbol_rates_list, combination)
            self.assertIsNone(data)

            # 给的rates数据不是同一个interval的
            rate22 = {'symbol': 'EURUSD', 'interval': '1m', 'ts': 1641394800, 'price_open': 2.250, 'price_high': 2.580,
                      'price_low': 2.490, 'price_closed': 2.560}
            symbol_rates_list = [rate1, rate22]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_strict_match(symbol_rates_list, combination)
            self.assertIsNone(data)

            # 给的rates数据ts相差超过1个interval
            rate22 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641398401, 'price_open': 2.250, 'price_high': 2.580,
                      'price_low': 2.490, 'price_closed': 2.560}
            symbol_rates_list = [rate1, rate22]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_strict_match(symbol_rates_list, combination)
            self.assertIsNone(data)

            # 给的rates数据ts相差小于1个interval
            rate22 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641394890, 'price_open': 2.250, 'price_high': 2.580,
                      'price_low': 2.490, 'price_closed': 2.560}
            symbol_rates_list = [rate1, rate22]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_strict_match(symbol_rates_list, combination)
            self.assertTrue(mode in data['symbol'])
            print(data)
            # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
            self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3,
                             data['price_open'])
            self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3,
                             data['price_high'])
            self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3,
                             data['price_low'])
            self.assertEqual(
                rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] / rate2_trio_price * 3,
                data['price_closed'])

    def test_calc_combo_price_best_effort(self):
        rate1 = {'symbol': 'XAUUSD', 'interval': '1h', 'ts': 1641394800, 'price_open': 1.6490, 'price_high': 1.6580,
                 'price_low': 1.6470, 'price_closed': 1.6530}
        rate2 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641394800, 'price_open': 2.250, 'price_high': 2.580,
                 'price_low': 2.490, 'price_closed': 2.560}
        ##### 方法内全局mock #########
        # 指定XAUUSD和EURUSD的3点价
        rate1_trio_price = 4.2
        rate2_trio_price = 5
        values = {1: Symbol(id=1, name='XAUUSD', symbol_value='XAUUSD', trio_point_price=rate1_trio_price),
                  4: Symbol(id=4, name='EURUSD', symbol_value='EURUSD', trio_point_price=rate2_trio_price)}
        mock_get_symbol_by_id = Mock(side_effect=lambda x: values.get(x))
        with patch('libs.database.Cache.get_symbol_by_id', mock_get_symbol_by_id):
            ############ best_effort #############
            # 正常计算
            symbol_rates_list = [rate1, rate2]
            mode = 'best_effort_match'
            combination = Combination(id=1, name='XAUUSD_EURUSD_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_best_effort_match(symbol_rates_list, combination)
            self.assertTrue(mode in data['symbol'])
            print(data)
            # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
            self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3,
                             data['price_open'])
            self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3,
                             data['price_high'])
            self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3,
                             data['price_low'])
            self.assertEqual(
                rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] / rate2_trio_price * 3,
                data['price_closed'])

            # 给的rates数据缺一个并且去拉时还拉不到
            symbol_rates_list = [rate1]
            combination = Combination(id=1, name='XAUUSD_EURUSD_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            get_lastest_price_before_dst_ts_none = Mock(return_value=None)
            with patch('libs.gen_combinations_price.get_lastest_price_before_dst_ts',
                       get_lastest_price_before_dst_ts_none):
                data = gen_combinations_price.calc_combo_price_best_effort_match(symbol_rates_list, combination)
                get_lastest_price_before_dst_ts_none.assert_called_once()  # 对应mock的方法一定调用过一次
                self.assertIsNone(data)

            # 给的rates数据缺一个并且去拉时，成功拉取到了一个同ts的数据
            symbol_rates_list = [rate1]
            combination = Combination(id=1, name='XAUUSD_EURUSD_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            get_lastest_price_before_dst_ts_valid = Mock(return_value=rate2)
            with patch('libs.gen_combinations_price.get_lastest_price_before_dst_ts',
                       get_lastest_price_before_dst_ts_valid):
                data = gen_combinations_price.calc_combo_price_best_effort_match(symbol_rates_list, combination)
                get_lastest_price_before_dst_ts_valid.assert_called_once()  # 对应mock的方法一定调用过一次
                self.assertTrue(mode in data['symbol'])
                print(data)
                # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
                self.assertEqual(
                    rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3,
                    data['price_open'])
                self.assertEqual(
                    rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3,
                    data['price_high'])
                self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3,
                                 data['price_low'])
                self.assertEqual(
                    rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] / rate2_trio_price * 3,
                    data['price_closed'])

            # 给的rates数据不是同一个interval的
            rate22 = {'symbol': 'EURUSD', 'interval': '1m', 'ts': 1641394800, 'price_open': 2.250, 'price_high': 2.580,
                      'price_low': 2.490, 'price_closed': 2.560}
            symbol_rates_list = [rate1, rate22]
            combination = Combination(id=1, name='XAUUSD_EURUSD_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_best_effort_match(symbol_rates_list, combination)
            self.assertIsNone(data)

            # 给的rates数据ts相差超过1个interval
            rate22 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641398401, 'price_open': 2.250, 'price_high': 2.580,
                      'price_low': 2.490, 'price_closed': 2.560}
            symbol_rates_list = [rate1, rate22]
            combination = Combination(id=1, name='XAUUSD_EURUSD_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            get_lastest_price_before_dst_ts_valid2 = Mock(return_value=rate2)
            with patch('libs.gen_combinations_price.get_lastest_price_before_dst_ts',
                       get_lastest_price_before_dst_ts_valid2):
                data = gen_combinations_price.calc_combo_price_best_effort_match(symbol_rates_list, combination)
                get_lastest_price_before_dst_ts_valid2.assert_called_once()  # 对应mock的方法一定调用过一次
                self.assertTrue(mode in data['symbol'])
                print(data)
                # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
                self.assertEqual(
                    rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3,
                    data['price_open'])
                self.assertEqual(
                    rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3,
                    data['price_high'])
                self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3,
                                 data['price_low'])
                self.assertEqual(
                    rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] / rate2_trio_price * 3,
                    data['price_closed'])

            # 给的rates数据ts相差小于1个interval
            rate22 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641394890, 'price_open': 2.250, 'price_high': 2.580,
                      'price_low': 2.490, 'price_closed': 2.560}
            symbol_rates_list = [rate1, rate22]
            combination = Combination(id=1, name='XAUUSD_EURUSD_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_best_effort_match(symbol_rates_list, combination)
            self.assertTrue(mode in data['symbol'])
            print(data)
            # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
            self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3,
                             data['price_open'])
            self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3,
                             data['price_high'])
            self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3,
                             data['price_low'])
            self.assertEqual(
                rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] / rate2_trio_price * 3,
                data['price_closed'])

    def test_update_historical_combined_data(self):
        start = datetime.datetime.strptime('2022-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime('2022-01-14 23:59:59', '%Y-%m-%d %H:%M:%S')
        combination_ids = [1]
        gen_combinations_price.update_historical_combined_data('1h', start, end, combination_ids)


if __name__ == '__main__':
    unittest.main()
