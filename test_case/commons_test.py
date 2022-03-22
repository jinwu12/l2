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


if __name__ == '__main__':
    unittest.main()