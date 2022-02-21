from libs import get_source_historical_data
from apscheduler.schedulers.background import BackgroundScheduler
import time
import datetime


# 开始的日期,由于是取的0点，所以需要往前一天以防漏掉周六早上那几个小时的数据
end = (datetime.datetime.now() + datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
# 七天前的日期
SevenDayAgo = (datetime.datetime.now() - datetime.timedelta(days = 6))
# 转换为时间戳
timeStamp = int(time.mktime(SevenDayAgo.timetuple()))
# 转换为其他字符串格式
start = SevenDayAgo.strftime("%Y-%m-%d")
print(start,end)


#初始化后台调度器
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

#添加调度器任务，每周六中午十二点执行数据补录
#小时级数据补录
scheduler.add_job(
        get_source_historical_data.get_span_historical_data,
        trigger='cron',
        day_of_week = 'sat',
        hour='12',
        args = [start, end, '1h'],
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
        args = [start, end, '1m'],
        max_instances=100,
        misfire_grace_time=60,
        coalesce=True
)

#启动调度器
scheduler.start()

while(True):
    time.sleep(1)
