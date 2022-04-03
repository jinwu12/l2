import argparse
from datetime import datetime

from libs import gen_combinations_price


def update_historical_combination_price(args):
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

    # 解析参数
    args = parser.parse_args()
    # 执行函数功能
    args.func(args)
