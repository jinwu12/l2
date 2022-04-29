import os
import logging
import sys
import unittest

sys.path.append("..")
from libs.database import *
from libs.gen_pivot_report import *

# 设置为测试环境
os.environ["env"] = "test"


record_secondary_rally = PivotReportRecord(pivot_report=1, date=1650128981, is_recorded=True,
                                           recorded_column=PivotReportColumn.SECONDARY_RALLY,
                                           is_pivot=True, price=10)
record_nature_rally = PivotReportRecord(pivot_report=2, date=1650128981, is_recorded=True,
                                        recorded_column=PivotReportColumn.NATURAL_RALLY,
                                        is_pivot=True, price=10)
record_up_trend = PivotReportRecord(pivot_report=3, date=1650128981, is_recorded=True,
                                    recorded_column=PivotReportColumn.UPWARD_TREND,
                                    is_pivot=True, price=10)
record_downward_trend = PivotReportRecord(pivot_report=4, date=1650128981, is_recorded=True,
                                          recorded_column=PivotReportColumn.DOWNWARD_TREND,
                                          is_pivot=True, price=10)
record_natural_reaction = PivotReportRecord(pivot_report=5, date=1650128981, is_recorded=True,
                                            recorded_column=PivotReportColumn.NATURAL_REACTION,
                                            is_pivot=True, price=10)
record_secondary_reaction = PivotReportRecord(pivot_report=6, date=1650128981, is_recorded=True,
                                              recorded_column=PivotReportColumn.SECONDARY_REACTION,
                                              is_pivot=True, price=10)


class GenPivotReport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("create tables...")
        config_db.create_tables([Symbol])
        data_source_db.create_tables([XauUsd, Dxy, DxyMt5, EurUsd, GbpUsd, Tnx, UsdCad, UsdChf, UsdJpy, UsdSek])
        production_combined_data_db.create_tables([CombinedSymbol])
        production_pivot_report_db.create_tables([PivotReportRecord])
        # 初始化数据
        print("init test data...")
        for record in [record_secondary_rally, record_nature_rally, record_up_trend, record_downward_trend,
                       record_natural_reaction, record_secondary_reaction]:
            record.save()
        # 配置peewee输出sql
        logger = logging.getLogger("peewee")
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

    def test_price_need_record(self):
        # 自然回升：大于等于记录，小于不记录
        self.assertTrue(price_need_record(10.1, record_nature_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_nature_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertFalse(price_need_record(9.998, record_nature_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        # 上升趋势：大于等于记录，小于不记录
        self.assertTrue(price_need_record(10.1, record_up_trend.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_up_trend.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertFalse(price_need_record(9.998, record_up_trend.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        # 下降趋势：小于等于记录，大于不记录
        self.assertFalse(price_need_record(10.1, record_downward_trend.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_downward_trend.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(9.998, record_downward_trend.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        # 自然回撤：小于等于记录，大于不记录
        self.assertFalse(price_need_record(10.1, record_natural_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_natural_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(9.998, record_natural_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        # 次级回升：大于等于记录，小于不记录
        self.assertTrue(price_need_record(10.1, record_secondary_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_secondary_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertFalse(price_need_record(9.998, record_secondary_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        # 次级回撤：小于等于记录，大于不记录
        self.assertFalse(price_need_record(10.1, record_secondary_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_secondary_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(9.998, record_secondary_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))

class testPivotReport(unittest.TestCase):

    def test_update_historical_pivot_point(self):
        
        #源：自然回升，目标：自然回撤
        data = update_historical_pivot_point(2, 5, 4, 1583956800)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [2, 3])
        self.assertEqual(data['pivot_point_date'], ['2020-03-10', '2020-02-18'])

        #源：自然回升，目标：上升趋势
        data = update_historical_pivot_point(2, 3, 4, 1581710400)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [5])
        self.assertEqual(data['pivot_point_date'], ['2020-02-09'])

        #源：上升趋势，目标：自然回撤
        data = update_historical_pivot_point(3, 5, 4, 1581969600)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [2, 3])
        self.assertEqual(data['pivot_point_date'], ['2020-02-13', '2020-02-15'])

        #源：下降趋势，目标：自然回升
        data = update_historical_pivot_point(4, 2, 4, 1583611200)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [5, 4])
        self.assertEqual(data['pivot_point_date'], ['2020-02-22', '2020-02-23'])

        #源：自然回撤，目标：自然回升
        data = update_historical_pivot_point(5, 2, 4, 1582056000)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [5, 4])
        self.assertEqual(data['pivot_point_date'], ['2020-02-17', '2020-02-02'])

        #源：自然回撤，目标：下降趋势
        data = update_historical_pivot_point(5, 4, 4, 1582488000)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [2])
        self.assertEqual(data['pivot_point_date'], ['2020-02-13'])

        #源：次级回撤，目标：自然回升
        data = update_historical_pivot_point(6, 2, 4, 1584820800)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [5, 4])
        self.assertEqual(data['pivot_point_date'], ['2020-03-18', '2020-03-09'])

        #源：次级回撤，目标：自然回撤
        data = update_historical_pivot_point(6, 5, 4, 1583784000)  
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [2, 3])
        self.assertEqual(data['pivot_point_date'], ['2020-03-07', '2020-02-18'])

        #源：次级回升，目标：自然回升
        data = update_historical_pivot_point(1, 2, 4, 1581624000)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [5, 4])
        self.assertEqual(data['pivot_point_date'], ['2020-02-09', '2020-02-02'])

        #源：次级回升，目标：自然回撤
        data = update_historical_pivot_point(1, 5, 4, 1584561600)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [2, 3])
        self.assertEqual(data['pivot_point_date'], ['2020-03-12', '2020-03-13'])

        # 待更新的2个关键点至少一个没有数据
        data = update_historical_pivot_point(2, 5, 4, 1581134400)
        print(data)
        self.assertTrue(data['result'])
        self.assertEqual(data['pivot_point_column'], [2])
        self.assertEqual(data['pivot_point_date'], ['2020-02-06'])

        #不符合更新关键点的条件
        data = update_historical_pivot_point(1, 3, 4, 1584561600)
        self.assertFalse(data['result'])


if __name__ == '__main__':
    unittest.main()
