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


if __name__ == '__main__':
    unittest.main()
