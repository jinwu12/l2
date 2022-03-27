import sys
sys.path.append('..')
from libs import fetcher

data = fetcher.get_historical_data_from_yfinance('^TNX','1h', '2022-03-25','2022-03-27','1d')

print(data)