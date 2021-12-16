from libs import commons
import schedule
import MetaTrader5 as mt5
from libs import get_realtime_data
import time

#初始化入库db
db = commons.db_connect()

#每分钟执行入库任务
schedule.every(1).minute.at(":01").do(get_realtime_data.update_realtime_data,interval='1m',db=db,mt5_account='5348288',mt5=mt5)

#每小时执行入库任务
schedule.every(1).hour.at('00:01').do(get_realtime_data.update_realtime_data,interval='1h',db=db,mt5_account='5348288',mt5=mt5)

while True:
    schedule.run_pending()
    time.sleep(1)

