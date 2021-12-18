from libs import commons
import schedule
import MetaTrader5 as mt5
from libs import get_realtime_data
import time
from apscheduler.schedulers.background import BackgroundScheduler

#初始化入库db
db = commons.db_connect()

#初始化后台调度器
scheduler = BackgroundScheduler()
scheduler.start()

#添加调度器任务
#每周周日23时0分0秒-周六凌晨2点，始执行实时更新method list中所有symbol的入库任务
#周日23点-周日0点
#分钟级数据
#小时级数据
#周六0点-周六2点
#分钟级数据
scheduler.add_job(
        get_realtime_data.update_realtime_data(),
        trigger='cron',
        day_of_week = '6',
        hour='0-2',
        minute='*/1',
        args=['1m',db,'5348288',mt5]
)
#小时级数据

'''
#每小时执行入库任务
schedule.every(1).hour.at('00:01').do(get_realtime_data.update_realtime_data,interval='1h',db=db,mt5_account='5348288',mt5=mt5)

while True:
    schedule.run_pending()
    time.sleep(1)
'''
