from libs import fetcher
from apscheduler.schedulers.background import BackgroundScheduler
import time
import datetime


# 初始化后台调度器
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')


def weekly_date_reupdate(interval):
    end = datetime.datetime.now() + datetime.timedelta(days=1)
    start = (datetime.datetime.now() - datetime.timedelta(days=6))
    fetcher.fetch_data(start, end, interval)
    print(start, end)


# 添加调度器任务，每周六中午十二点执行数据补录
# 小时级数据补录
scheduler.add_job(
    weekly_date_reupdate,
    trigger='cron',
    day_of_week='sat',
    hour='12',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)
# 分钟级数据补录
scheduler.add_job(
    weekly_date_reupdate,
    trigger='cron',
    day_of_week='sat',
    hour='13',
    args=['1m'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

# 启动调度器
scheduler.start()

while True:
    time.sleep(1)
