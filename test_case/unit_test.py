import sys
sys.path.append("..")
import unittest
from libs.database import *
from libs import gen_combinations_price
import datetime
import json
from unittest.mock import Mock, patch
from playhouse.shortcuts import model_to_dict



class TestFunctions(unittest.TestCase):

    def test_get_lastest_price_before_dst_ts(self):
        dst_ts = 1641160800
        result = gen_combinations_price.get_lastest_price_before_dst_ts(
            "DX-Y.NYB", "1h", dst_ts)
        # print(result)
        self.assertEqual("DX-Y.NYB", result['symbol'])
        self.assertEqual(dst_ts, result['ts'])
        self.assertEqual(95.67, result['price_open'])
        self.assertEqual(95.67, result['price_high'])
        self.assertEqual(95.67, result['price_low'])
        self.assertEqual(95.67, result['price_closed'])

        result = gen_combinations_price.get_lastest_price_before_dst_ts(
            "DX-Y.NYB", "1h", 0)
        self.assertTrue(result is None)

    def test_group_rates_by_ts(self):
        symbol1 = Symbol(id=1, name='XAUUSD',
                         symbol_value='XAUUSD', trio_point_price=5)
        symbol2 = Symbol(id=4, name='EURUSD',
                         symbol_value='EURUSD', trio_point_price=6)
        symbol3 = Symbol(id=3, name='DXY', symbol_value='DXY',
                         trio_point_price=7)
        ts1 = 1577970000
        ts2 = 1577973600
        ts3 = 1577977200
        tss = [ts1, ts2, ts3]

        rate11 = {'symbol_name': 'XAUUSD', 'interval': '1h', 'ts': ts1, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        rate12 = {'symbol_name': 'XAUUSD', 'interval': '1h', 'ts': ts2, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        rate13 = {'symbol_name': 'XAUUSD', 'interval': '1h', 'ts': ts3, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}

        # symbol中存在至少1个ts为非标时间（小于1个interval或大于1个interval）
        rate21 = {'symbol_name': 'EURUSD', 'interval': '1h', 'ts': ts1+1, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        rate31 = {'symbol_name': 'DXY', 'interval': '1h', 'ts': ts1+3601, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        start = 1577970000
        end = 1577974000
        symbols = [symbol1, symbol2, symbol3]
        data = {'XAUUSD': [rate11], 'EURUSD': [rate21], 'DXY': [rate31]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(1, len(results))
        self.assertEqual(1, len(results[0]))
        self.assertEqual(ts1, results[0][0]['ts'])

        # 一个symbol一个ts
        start = 1577970000
        end = 1577970000
        symbols = [symbol1]
        data = {'XAUUSD': [rate11]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(1, len(results))
        self.assertEqual(ts1, results[0][0]['ts'])

        # 一个symbol多个ts
        start = 1577970000
        end = 1577977200
        symbols = [symbol1]
        data = {'XAUUSD': [rate11, rate12, rate13]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(3, len(results))
        for i in range(3):
            self.assertEqual(tss[i], results[i][0]['ts'])

        # 2个symbol一个相同ts
        rate21 = {'symbol_name': 'EURUSD', 'interval': '1h', 'ts': ts1, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        start = 1577970000
        end = 1577970000
        symbols = [symbol1, symbol2]
        data = {'XAUUSD': [rate11], 'EURUSD': [rate21]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(1, len(results))
        self.assertEqual(ts1, results[0][0]['ts'])
        self.assertEqual(ts1, results[0][1]['ts'])

        # 多个symbol一个相同ts
        rate31 = {'symbol_name': 'DXY', 'interval': '1h', 'ts': ts1, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        start = 1577970000
        end = 1577970000
        symbols = [symbol1, symbol2, symbol3]
        data = {'XAUUSD': [rate11], 'EURUSD': [rate21], 'DXY': [rate31]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(1, len(results))
        for i in range(len(symbols)):
            self.assertEqual(ts1, results[0][i]['ts'])

        # 2个symbol一个不同ts
        start = 1577970000
        end = 1577974000
        symbols = [symbol1, symbol3]
        data = {'XAUUSD': [rate12], 'DXY': [rate31]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(2, len(results))
        for i in range(2):
            self.assertEqual(1, len(results[i]))
            self.assertEqual(tss[i], results[i][0]['ts'])

        # 2个symbol有多个相等的ts
        rate32 = {'symbol_name': 'DXY', 'interval': '1h', 'ts': ts2, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        rate33 = {'symbol_name': 'DXY', 'interval': '1h', 'ts': ts3, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        start = 1577970000
        end = 1577978000
        symbols = [symbol1, symbol3]
        data = {'XAUUSD': [rate11, rate12, rate13],
                'DXY': [rate31, rate32, rate33]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(3, len(results))
        for i in range(3):
            self.assertEqual(2, len(results[i]))
            for j in range(len(results[i])):
                self.assertEqual(tss[i], results[i][j]['ts'])

        # 2个symbol的ts个数不相等,至少有一个ts在所有symbol中均存在报价点
        start = 1577970000
        end = 1577978000
        symbols = [symbol1, symbol3]
        data = {'XAUUSD': [rate11, rate12, rate13], 'DXY': [rate31, rate32]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(3, len(results))
        self.assertEqual(2, len(results[0]))
        self.assertEqual(2, len(results[1]))
        self.assertEqual(1, len(results[2]))
        for i in range(len(results)):
            for j in range(len(results[i])):
                self.assertEqual(tss[i], results[i][j]['ts'])

        # 2个symbol的ts个数不相等,每个ts只有一个symbol中均存在报价点
        start = 1577970000
        end = 1577978000
        symbols = [symbol1, symbol3]
        data = {'XAUUSD': [rate11, rate13], 'DXY': [rate32]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(3, len(results))
        for i in range(len(results)):
            self.assertEqual(1, len(results[i]))
            self.assertEqual(tss[i], results[i][0]['ts'])

        # 多个symbol均有1个ts,至少有一个symbol的ts与其它symbol的ts不相等
        start = 1577970000
        end = 1577978000
        symbols = [symbol1, symbol2, symbol3]
        data = {'XAUUSD': [rate11], 'EURUSD': [rate21], 'DXY': [rate32]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(2, len(results))
        self.assertEqual(2, len(results[0]))
        self.assertEqual(1, len(results[1]))
        for i in range(len(results)):
            for j in range(len(results[i])):
                self.assertEqual(tss[i], results[i][j]['ts'])

        # 多个symbol有多个相等的ts
        rate22 = {'symbol_name': 'EURUSD', 'interval': '1h', 'ts': ts2, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        rate23 = {'symbol_name': 'EURUSD', 'interval': '1h', 'ts': ts3, 'price_open': 1.0, 'price_high': 1.0, 'price_low': 1.0,
                  'price_closed': 1.0}
        start = 1577970000
        end = 1577978000
        symbols = [symbol1, symbol2, symbol3]
        data = {'XAUUSD': [rate11, rate12, rate13], 'EURUSD': [
            rate21, rate22, rate23], 'DXY': [rate31, rate32, rate33]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(3, len(results))
        for i in range(3):
            self.assertEqual(3, len(results[i]))
            for j in range(len(results[i])):
                self.assertEqual(tss[i], results[i][j]['ts'])

        # 多个symbol有相同数量的ts，至少有一个symbol的ts列表中有一个ts与其它symbol的ts列表中的所有值均不相等

        start = 1577970000
        end = 1577978000
        symbols = [symbol1, symbol2, symbol3]
        data = {'XAUUSD': [rate11, rate12], 'EURUSD': [
            rate21, rate22], 'DXY': [rate32, rate33]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(3, len(results))
        self.assertEqual(2, len(results[0]))
        self.assertEqual(3, len(results[1]))
        self.assertEqual(1, len(results[2]))
        for i in range(3):

            for j in range(len(results[i])):
                self.assertEqual(tss[i], results[i][j]['ts'])

        # 多个symbol至少有一个symbol的ts列表数量与其它symbol不相等，至少有一个ts在所有symbol中均存在报价点

        start = 1577970000
        end = 1577978000
        symbols = [symbol1, symbol2, symbol3]
        data = {'XAUUSD': [rate11, rate12, rate13], 'EURUSD': [
            rate21, rate22], 'DXY': [rate32, rate33]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(3, len(results))
        self.assertEqual(2, len(results[0]))
        self.assertEqual(3, len(results[1]))
        self.assertEqual(2, len(results[2]))
        for i in range(3):

            for j in range(len(results[i])):
                self.assertEqual(tss[i], results[i][j]['ts'])

        # 多个symbol至少有一个symbol的ts列表数量与其它symbol不相等，所有的ts均只在一个symbol中存在报价点

        start = 1577970000
        end = 1577978000
        symbols = [symbol1, symbol2, symbol3]
        data = {'XAUUSD': [rate11, rate12], 'EURUSD': [], 'DXY': [rate33]}
        results = gen_combinations_price.group_rates_by_ts(
            start, end, '1h', symbols, data)
        self.assertEqual(3, len(results))
        for i in range(3):
            self.assertEqual(1, len(results[i]))
            for j in range(len(results[i])):
                self.assertEqual(tss[i], results[i][j]['ts'])

    def test_calculate_combination_3point_price(self):
        combination = Combination(
            id=1, symbol_list="1,10", combination_3point_price=6)
        self.assertEqual(
            6, gen_combinations_price.calculate_combination_3point_price(combination))
        combination = Combination(id=1, symbol_list="1,10")
        self.assertEqual(
            6, gen_combinations_price.calculate_combination_3point_price(combination))

    def test_check_combinations(self):
        gen_combinations_price.check_combinations()

    def test_calc_combo_price_strict_match(self):
        rate1 = {'symbol': 'XAUUSD', 'interval': '1h', 'ts': 1641394800, 'price_open': 1.6490, 'price_high': 1.6580,
                 'price_low': 1.6470, 'price_closed': 1.6530}
        rate12 = {'symbol': 'XAUUSD', 'interval': '1h', 'ts': 1641394890, 'price_open': 1.350, 'price_high': 1.680,
                  'price_low': 1.790, 'price_closed': 1.660}  # ts相差小于1个interval
        rate2 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641394800, 'price_open': 2.250, 'price_high': 2.580,
                 'price_low': 2.490, 'price_closed': 2.560}
        rate21 = {'symbol': 'EURUSD', 'interval': '1m', 'ts': 1641394800, 'price_open': 2.350, 'price_high': 2.680,
                  'price_low': 2.790, 'price_closed': 2.660}  # interval不同
        rate22 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641394890, 'price_open': 2.350, 'price_high': 2.680,
                  'price_low': 2.790, 'price_closed': 2.660}  # ts相差小于1个interval
        rate23 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641398401, 'price_open': 2.250, 'price_high': 2.580,
                  'price_low': 2.490, 'price_closed': 2.560}  # ts相差大于1个interval
        rate3 = {'symbol': 'DXY', 'interval': '1h', 'ts': 1641394800, 'price_open': 2.780, 'price_high': 3.100,
                 'price_low': 2.690, 'price_closed': 2.900}
        ##### mock #########
        # 指定XAUUSD，DXY和EURUSD的3点价
        rate1_trio_price = 4.2
        rate2_trio_price = 5
        rate3_trio_price = 5.5
        values = {1: Symbol(id=1, name='XAUUSD', symbol_value='XAUUSD', trio_point_price=rate1_trio_price),
                  4: Symbol(id=4, name='EURUSD', symbol_value='EURUSD', trio_point_price=rate2_trio_price),
                  7: Symbol(id=7, name='DXY', symbol_value='DXY', trio_point_price=rate3_trio_price),
                  11: Symbol(id=1, name='XAUUSD', symbol_value='XAUUSD', trio_point_price=None)}
        mock_get_symbol_by_id = Mock(side_effect=lambda x: values.get(x))
        with patch('libs.database.Cache.get_symbol_by_id', mock_get_symbol_by_id):
            ############ strict_match #############
            # symbol_rates_list数据等于combination.symbol_list且ts相同
            symbol_rates_list = [rate1, rate2, rate3]
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4,7')
            mode = 'strict_match'
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertIsNotNone(data)
            self.assertTrue(mode in data['symbol'])
            print(data)
            # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
            self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3 + rate3['price_open'] / rate3_trio_price * 3,
                             data['price_open'])
            self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3+rate3['price_high'] / rate3_trio_price * 3,
                             data['price_high'])
            self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3 + rate3['price_low'] / rate3_trio_price * 3,
                             data['price_low'])
            self.assertEqual(
                rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] /
                rate2_trio_price * 3 +
                rate3['price_closed'] / rate3_trio_price * 3,
                data['price_closed'])

            # symbol_rates_list数据等于combination.symbol_list但又不完整
            symbol_rates_list = [rate1, rate2]
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='4,7')
            mode = 'strict_match'
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertIsNone(data)

            # symbol_rates_list数据等于combination.symbol_list，但ts不同
            # ts相差超过1个interval
            symbol_rates_list = [rate12, rate23, rate3]
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4,7')
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertIsNone(data)

            # ts相差小于1个interval
            symbol_rates_list = [rate1, rate22, rate3]
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4,7')
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertTrue(mode in data['symbol'])
            print(data)
            # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
            self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate22['price_open'] / rate2_trio_price * 3 + rate3['price_open'] / rate3_trio_price * 3,
                             data['price_open'])
            self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate22['price_high'] / rate2_trio_price * 3+rate3['price_high'] / rate3_trio_price * 3,
                             data['price_high'])
            self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate22['price_low'] / rate2_trio_price * 3 + rate3['price_low'] / rate3_trio_price * 3,
                             data['price_low'])
            self.assertEqual(
                rate1['price_closed'] / rate1_trio_price * 3 + rate22['price_closed'] /
                rate2_trio_price * 3 +
                rate3['price_closed'] / rate3_trio_price * 3,
                data['price_closed'])
            self.assertEqual(1641394800, data['ts'])

            # symbol_rates_list数据少于combination.symbol_list
            symbol_rates_list = [rate2]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertIsNone(data)

            # symbol_rates_list缺少3点价格数据
            mbol_rates_list = [rate1, rate2]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='11,4')
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertIsNone(data)

            # 给的rates数据不是同一个interval的
            symbol_rates_list = [rate1, rate21]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertIsNone(data)

    def test_calc_combo_price_best_effort(self):
        rate1 = {'symbol': 'XAUUSD', 'interval': '1h', 'ts': 1641394800, 'price_open': 1.6490, 'price_high': 1.6580,
                 'price_low': 1.6470, 'price_closed': 1.6530}
        rate12 = {'symbol': 'XAUUSD', 'interval': '1h', 'ts': 1641394890, 'price_open': 1.350, 'price_high': 1.680,
                  'price_low': 1.790, 'price_closed': 1.660}  # ts相差小于1个interval
        rate2 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641394800, 'price_open': 2.250, 'price_high': 2.580,
                 'price_low': 2.490, 'price_closed': 2.560}
        rate21 = {'symbol': 'EURUSD', 'interval': '1m', 'ts': 1641394800, 'price_open': 2.350, 'price_high': 2.680,
                  'price_low': 2.790, 'price_closed': 2.660}  # interval不同
        rate22 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641394890, 'price_open': 2.350, 'price_high': 2.680,
                  'price_low': 2.790, 'price_closed': 2.660}  # ts相差小于1个interval
        rate23 = {'symbol': 'EURUSD', 'interval': '1h', 'ts': 1641398401, 'price_open': 2.250, 'price_high': 2.580,
                  'price_low': 2.490, 'price_closed': 2.560}  # ts相差大于1个interval
        rate3 = {'symbol': 'DXY', 'interval': '1h', 'ts': 1641394800, 'price_open': 2.780, 'price_high': 3.100,
                 'price_low': 2.690, 'price_closed': 2.900}
        ##### 方法内全局mock #########
        # 指定XAUUSD，DXY和EURUSD的3点价
        rate1_trio_price = 4.2
        rate2_trio_price = 5
        rate3_trio_price = 5.5
        values = {1: Symbol(id=1, name='XAUUSD', symbol_value='XAUUSD', trio_point_price=rate1_trio_price),
                  4: Symbol(id=4, name='EURUSD', symbol_value='EURUSD', trio_point_price=rate2_trio_price),
                  7: Symbol(id=7, name='DXY', symbol_value='DXY', trio_point_price=rate3_trio_price),
                  11: Symbol(id=1, name='XAUUSD', symbol_value='XAUUSD', trio_point_price=None)}
        mock_get_symbol_by_id = Mock(side_effect=lambda x: values.get(x))
        with patch('libs.database.Cache.get_symbol_by_id', mock_get_symbol_by_id):
            ############ best_effort #############
            # symbol_rates_list数据等于combination.symbol_list且ts相同
            symbol_rates_list = [rate1, rate2, rate3]
            mode = 'best_effort_match'
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4,7')
            data = gen_combinations_price.calc_combo_price_best_effort_match(
                symbol_rates_list, combination)
            self.assertTrue(mode in data['symbol'])
            print(data)
            # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
            self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3 + rate3['price_open'] / rate3_trio_price * 3,
                             data['price_open'])
            self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3+rate3['price_high'] / rate3_trio_price * 3,
                             data['price_high'])
            self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3 + rate3['price_low'] / rate3_trio_price * 3,
                             data['price_low'])
            self.assertEqual(
                rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] /
                rate2_trio_price * 3 +
                rate3['price_closed'] / rate3_trio_price * 3,
                data['price_closed'])

            # symbol_rates_list数据等于combination.symbol_list,但ts相差超过1个interval
            symbol_rates_list = [rate1, rate23, rate3]
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4,7')
            get_lastest_price_before_dst_ts_valid2 = Mock(return_value=rate2)
            with patch('libs.gen_combinations_price.get_lastest_price_before_dst_ts',
                       get_lastest_price_before_dst_ts_valid2):
                data = gen_combinations_price.calc_combo_price_best_effort_match(
                    symbol_rates_list, combination)
                get_lastest_price_before_dst_ts_valid2.assert_called_once()  # 对应mock的方法一定调用过一次
                self.assertTrue(mode in data['symbol'])
                print(data)
                # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
                self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3 + rate3['price_open'] / rate3_trio_price * 3,
                                 data['price_open'])
                self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3+rate3['price_high'] / rate3_trio_price * 3,
                                 data['price_high'])
                self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3 + rate3['price_low'] / rate3_trio_price * 3,
                                 data['price_low'])
                self.assertEqual(rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] / rate2_trio_price * 3 + rate3['price_closed'] / rate3_trio_price * 3,
                                 data['price_closed'])

            # 给的rates数据ts相差小于1个interval
            symbol_rates_list = [rate1, rate22, rate3]
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4,7')
            data = gen_combinations_price.calc_combo_price_best_effort_match(
                symbol_rates_list, combination)
            self.assertTrue(mode in data['symbol'])
            print(data)
            self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate22['price_open'] / rate2_trio_price * 3 + rate3['price_open'] / rate3_trio_price * 3,
                             data['price_open'])
            self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate22['price_high'] / rate2_trio_price * 3+rate3['price_high'] / rate3_trio_price * 3,
                             data['price_high'])
            self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate22['price_low'] / rate2_trio_price * 3 + rate3['price_low'] / rate3_trio_price * 3,
                             data['price_low'])
            self.assertEqual(
                rate1['price_closed'] / rate1_trio_price * 3 + rate22['price_closed'] /
                rate2_trio_price * 3 +
                rate3['price_closed'] / rate3_trio_price * 3,
                data['price_closed'])
            self.assertEqual(1641394800, data['ts'])

            # symbol_rates_list数据少于combination.symbol_list并且去拉时还拉不到
            symbol_rates_list = [rate1, rate2]
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4,7')
            get_lastest_price_before_dst_ts_none = Mock(return_value=None)
            with patch('libs.gen_combinations_price.get_lastest_price_before_dst_ts',
                       get_lastest_price_before_dst_ts_none):
                data = gen_combinations_price.calc_combo_price_best_effort_match(
                    symbol_rates_list, combination)
                get_lastest_price_before_dst_ts_none.assert_called_once()  # 对应mock的方法一定调用过一次
                self.assertIsNone(data)

            # symbol_rates_list数据少于combination.symbol_list，成功拉取到了同ts的数据
            symbol_rates_list = [rate1, rate2]
            combination = Combination(id=1, name='XAUUSD_EURUSD_DXY_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4,7')
            get_lastest_price_before_dst_ts_valid = Mock(return_value=rate3)
            with patch('libs.gen_combinations_price.get_lastest_price_before_dst_ts',
                       get_lastest_price_before_dst_ts_valid):
                data = gen_combinations_price.calc_combo_price_best_effort_match(
                    symbol_rates_list, combination)
                get_lastest_price_before_dst_ts_valid.assert_called_once()  # 对应mock的方法一定调用过一次
                self.assertTrue(mode in data['symbol'])
                print(data)
                # 计算组合价: 计算组合价格=∑[(symbol价格/symbol 3point_price)*3]  先*3再求和
                self.assertEqual(rate1['price_open'] / rate1_trio_price * 3 + rate2['price_open'] / rate2_trio_price * 3 + rate3['price_open'] / rate3_trio_price * 3,
                                 data['price_open'])
                self.assertEqual(rate1['price_high'] / rate1_trio_price * 3 + rate2['price_high'] / rate2_trio_price * 3+rate3['price_high'] / rate3_trio_price * 3,
                                 data['price_high'])
                self.assertEqual(rate1['price_low'] / rate1_trio_price * 3 + rate2['price_low'] / rate2_trio_price * 3 + rate3['price_low'] / rate3_trio_price * 3,
                                 data['price_low'])
                self.assertEqual(rate1['price_closed'] / rate1_trio_price * 3 + rate2['price_closed'] / rate2_trio_price * 3 + rate3['price_closed'] / rate3_trio_price * 3,
                                 data['price_closed'])

            # symbol_rates_list缺少3点价格数据
            symbol_rates_list = [rate1, rate2]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='11,4')
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertIsNone(data)

            # symbol_rates_list没有combination.symbol_list中的数据
            symbol_rates_list = [rate3]
            combination = Combination(id=1, name='XAUUSD_EURUSD_strict_match', combined_method='strict_match',
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_strict_match(
                symbol_rates_list, combination)
            self.assertIsNone(data)

            # symbol_rates_list数据不是同一个interval的
            symbol_rates_list = [rate1, rate21]
            combination = Combination(id=1, name='XAUUSD_EURUSD_best_effort', combined_method=mode,
                                      combination_3point_price=6, trading_symbol='usd', symbol_list='1,4')
            data = gen_combinations_price.calc_combo_price_best_effort_match(
                symbol_rates_list, combination)
            self.assertIsNone(data)


    def test_update_historical_combined_data(self):
        start = datetime.datetime.strptime(
            '2022-01-03 00:00:00', '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(
            '2022-01-05 23:59:59', '%Y-%m-%d %H:%M:%S')
        combination_ids = [1]
        gen_combinations_price.update_historical_combined_data(
                '1h', start, end,combination_ids)

if __name__ == '__main__':
    unittest.main()
