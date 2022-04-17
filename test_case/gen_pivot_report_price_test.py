import logging
import sys
import unittest

sys.path.append("..")
import os

# 设置为测试环境
os.environ["env"] = "test"
from libs.gen_pivot_report import *

from libs.database import *

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
        self.assertFalse(
            price_need_record(10.1, record_natural_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_natural_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(
            price_need_record(9.998, record_natural_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        # 次级回升：大于等于记录，小于不记录
        self.assertTrue(price_need_record(10.1, record_secondary_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_secondary_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertFalse(
            price_need_record(9.998, record_secondary_rally.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        # 次级回撤：小于等于记录，大于不记录
        self.assertFalse(
            price_need_record(10.1, record_secondary_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(price_need_record(10, record_secondary_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))
        self.assertTrue(
            price_need_record(9.998, record_secondary_reaction.pivot_report, PivotReportColumn.DOWNWARD_TREND))

    def test_determine_column(self):
        # 传入价格（今日收盘价）比自然回升栏（2）最新一个关键点价格高3点或更多则切换到上升趋势栏
        record1 = PivotReportRecord(pivot_report=1001, date=1650128980, recorded_column=PivotReportColumn.NATURAL_RALLY,
                                    is_pivot=True, is_recorded=True, price=10)
        record1_1 = PivotReportRecord(pivot_report=1001, date=1650128900,
                                      recorded_column=PivotReportColumn.NATURAL_RALLY,
                                      is_pivot=True, is_recorded=True, price=17)
        for record in [record1, record1_1]:
            record.save()
        self.assertEqual(PivotReportColumn.UPWARD_TREND, determine_column(record1, 13, 3))


if __name__ == '__main__':
    unittest.main()
