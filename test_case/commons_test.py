import datetime
import unittest
import pytz
from libs.commons import *


class MyTestCase(unittest.TestCase):
    def test_datetime_str_with_timezone_to_timestamp(self):
        ts = datetime_str_with_timezone_to_timestamp("2022-02-16 09:36:00-05:00")
        self.assertEqual(1645022160, ts)

    def test_timestamp_to_datetime_str(self):
        datetime_str = timestamp_to_datetime_str(1645022160, "US/Eastern", "%Y-%m-%d %H:%M:%S")
        self.assertEqual("2022-02-16 09:36:00", datetime_str)
        self.assertEqual("2022-02-17 08:20:00",
                         timestamp_to_datetime_str(1645104000, "US/Eastern", "%Y-%m-%d %H:%M:%S"))

    def test_datetime_to_timestamp(self):
        ts = datetime_to_timestamp("2022-02-16 09:36:00", "US/Eastern")
        self.assertEqual(1645022160, ts)

    def test_check_and_fix_timestamp(self):
        self.assertEqual(1645022160, check_and_fix_timestamp(1645022160, '1m'))
        self.assertEqual(1645022160, check_and_fix_timestamp(1645022169, '1m'))
        self.assertEqual(1645022160, check_and_fix_timestamp(1645022199, '1m'))
        self.assertEqual(1647608400, check_and_fix_timestamp(1647608400, '1h'))
        self.assertEqual(1647608400, check_and_fix_timestamp(1647608499, '1h'))
        self.assertEqual(1647608400, check_and_fix_timestamp(1647608999, '1h'))

    def test_get_timezone_timestamp_offset(self):
        self.assertEqual(0, get_timezone_timestamp_offset('UTC'))
        self.assertEqual(0, get_timezone_timestamp_offset('ETC/UTC'))
        self.assertEqual(3*60*60, get_timezone_timestamp_offset('ETC/GMT-3'))
        self.assertEqual(8*60*60, get_timezone_timestamp_offset('ETC/GMT-8'))
        self.assertEqual(-8*60*60, get_timezone_timestamp_offset('ETC/GMT+8'))


if __name__ == '__main__':
    unittest.main()
