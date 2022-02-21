from libs import get_source_historical_data
from apscheduler.schedulers.background import BackgroundScheduler
import time
import datetime


# 今天的日期
today = datetime.datetime.now().strftime("%Y-%m-%d")
# 七天前的日期
SevenDayAgo = (datetime.datetime.now() - datetime.timedelta(days = 7))
# 转换为时间戳
timeStamp = int(time.mktime(SevenDayAgo.timetuple()))
# 转换为其他字符串格式
SevenDayAgoStr = SevenDayAgo.strftime("%Y-%m-%d")
print(today,SevenDayAgoStr)


#初始化后台调度器
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

#添加调度器任务，每周六中午十二点执行数据补录
#小时级数据补录
scheduler.add_job(
        get_source_historical_data.get_span_historical_data,
        trigger='cron',
        day_of_week = 'sat',
        hour='12',
        args = [SevenDayAgoStr, today, '1h'],
        max_instances=100,
        misfire_grace_time=60,
        coalesce=True
)
#分钟级数据补录
scheduler.add_job(
        get_source_historical_data.get_span_historical_data,
        trigger='cron',
        day_of_week = 'sat',
        hour='13',
        args = [SevenDayAgoStr, today, '1m'],
        max_instances=100,
        misfire_grace_time=60,
        coalesce=True
)

#启动调度器
scheduler.start()

while(True):
    time.sleep(1)
