#!/usr/bin/python
# -*- coding: utf-8


import argparse
import time
from datetime import datetime, timedelta
import pytz

from libs import gen_combinations_price
from libs.fetcher import get_historical_data_from_mt5, get_historical_data_from_yfinance, get_dxy_from_mt5
from libs.database import *


def update_historical_combination_price(args):
    """更新历史组合价格数据"""
    if args.debug:  # 开启了调试
        print(args)
    start = None
    end = None
    try:
        start = datetime.strptime(args.start, '%Y-%m-%d %H:%M:%S')
    except:
        start = datetime.strptime(args.start, '%Y-%m-%d')

    try:
        end = datetime.strptime(args.end, '%Y-%m-%d %H:%M:%S')
    except:
        end = datetime.strptime(args.end, '%Y-%m-%d')

    combination_ids = []
    if len(args.combinations) > 0:
        combination_ids = args.combinations.split(',')
    gen_combinations_price.update_historical_combined_data(args.interval, start, end, combination_ids)


def get_symbol_price(args):
    """获取指定symbol实时价格数据"""
    if args.debug:  # 开启了调试
        print(args)
    interval = args.interval
    symbols = Symbol.select()
    while True:
        for symbol in symbols:
            if symbol.symbol_value not in args.symbol:
                continue
            symbol_name = symbol.name
            # 根据symbol name获取拉取数据用的symbol value，用于获取数据
            symbol_value = symbol.symbol_value
            method = symbol.method
            timezone = symbol.timezone
            # 拉取yfinance数据源的symbol数据
            if method == 'get_historical_data_from_yfinance':
                # 实时数据拉取的start和end必须只传到日为止，比如2022-03-21，不能在后面带时分秒，否则会报错
                yf_start_time = datetime.now().date()
                yf_end_time = yf_start_time + timedelta(days=1)
                # yfinance的分钟级及小时级数据拉取逻辑一致
                # 拉取数据，并截取最后一个元素作为结果
                try:
                    print(get_historical_data_from_yfinance(
                        symbol_value, interval, yf_start_time, yf_end_time, '1d')[-1])
                except:
                    print("%s:数据拉取失败@%s" % symbol_value, str(yf_start_time) + "~" + str(yf_end_time))
            # 拉取mt5数据的symbol数据
            elif method == 'get_historical_data_from_mt5':
                mt5_tz = pytz.timezone(timezone)
                # 开始时间为当前时间减去interval
                if interval == '1m':
                    mt5_start_time = datetime.now(tz=mt5_tz).replace(second=0, microsecond=0) - timedelta(minutes=1)
                else:
                    mt5_start_time = datetime.now(tz=mt5_tz).replace(minute=0, second=0, microsecond=0) - timedelta(
                        hours=1)
                # 结束时间等于开始时间
                mt5_end_time = mt5_start_time
                # 拉取数据
                try:
                    print(
                        get_historical_data_from_mt5(symbol_value, symbol.timezone, interval, mt5_start_time,
                                                     mt5_end_time)[
                            0])
                except IndexError:
                    print("%s:数据拉取失败@%s" % symbol_value, str(mt5_start_time) + "~" + str(mt5_end_time))

            # 从mt5拉取数据去生成的symbol数据,当前只有dxy，如果有需要就继续在此分支下添加if即可
            if method == 'originate_from_mt5':
                mt5_tz = pytz.timezone(timezone)
                # 开始时间为当前时间减去interval
                if interval == '1m':
                    mt5_start_time = datetime.now(tz=mt5_tz).replace(second=0, microsecond=0) - timedelta(minutes=1)
                else:
                    mt5_start_time = datetime.now(tz=mt5_tz).replace(minute=0, second=0, microsecond=0) - timedelta(
                        hours=1)
                    # 结束时间与开始时间相等
                mt5_end_time = mt5_start_time
                # 根据mt5等货币对报价，生成DXY
                try:
                    print(get_dxy_from_mt5(mt5_start_time, mt5_end_time, interval))
                except IndexError:
                    print("%s:数据拉取失败@%s", symbol_value, str(mt5_start_time) + "~" + str(mt5_end_time))
        time.sleep(60)


def sync_database(args):
    data = {}
    models = Model.__subclasses__()
    models.extend(BaseSymbolPrice.__subclasses__())
    for sc in models:
        if sc != BaseSymbolPrice:
            alist = data.get(sc._meta.database)
            if alist is None:
                alist = []
            alist.append(sc)
            data[sc._meta.database] = alist
    tables = []
    for db in data.keys():
        tables.extend(db.get_tables())
    for db, alist in data.items():
        for model in alist:
            table_name = model._meta.table_name
            if table_name not in tables:
                print("create table", table_name)
                db.create_tables([model])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="l2量化交易cli", usage="%(prog)s [options]", add_help=False)

    # 选项配置
    parser.add_argument('-h', '--help', action='help', help="显示帮助信息")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.01', help="显示版本号")
    parser.add_argument('-d', '--debug', action='store_true', help="开启调试")

    # 子命令
    subparser = parser.add_subparsers(title='子命令', help="子命令帮助")

    # 子命令：更新组合历史价格hsp(historical_combination_price)
    parser_his_comb_price = subparser.add_parser('hcp', help='更新组合历史价格')
    parser_his_comb_price.add_argument('start', type=str, help='开始时间，如2022-01-01')
    parser_his_comb_price.add_argument('end', type=str, help='结束时间，如2022-02-01')
    parser_his_comb_price.add_argument('-interval', type=str, default='1h', help='间隔时间：[1h, 1m]')
    parser_his_comb_price.add_argument('-combinations', type=str, default='', help='指定要更新的组合id列表，逗号分隔，如：1,2,3')
    parser_his_comb_price.set_defaults(func=update_historical_combination_price)

    # 子命令：获取实时symbol价格数据(仅显示，不入库)
    parser_symbol_price = subparser.add_parser('price', help='获取实时symbol价格数据')
    parser_symbol_price.add_argument('-interval', type=str, default='1h', help='间隔时间：[1h, 1m]')
    parser_symbol_price.add_argument('symbol', nargs='*', default='XAUUSD', help='symbols，支持多个指定(空格分隔)')
    parser_symbol_price.set_defaults(func=get_symbol_price)

    # 子命令：同步数据库(创建表)
    parser_sync_database = subparser.add_parser('sync_db', help='同步(创建)数据库表')
    parser_sync_database.set_defaults(func=sync_database)

    # 解析参数
    args = parser.parse_args()
    # 执行函数功能
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
