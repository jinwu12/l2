from libs import fetcher
from apscheduler.schedulers.background import BackgroundScheduler
import time

# 初始化后台调度器
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

# 添加调度器任务
# 每周周日23时0分0秒-周六凌晨2点，始执行实时更新method list中所有symbol的入库任务
# 周日23点-周日0点
# 分钟级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='sun',
    hour='23',
    minute='0-59',
    args=['1m'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)
# 小时级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='sun',
    hour='23',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

# 周一0点～周五23点
# 分钟级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='mon-fri',
    hour='0-23',
    minute='0-59',
    args=['1m'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True

)
# 小时级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='mon-fri',
    hour='0-23',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

# 周六0点-周六3点
# 分钟级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='sat',
    hour='0-9',
    minute='0-59',
    args=['1m'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)
# 小时级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='sat',
    hour='0-9',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

# 启动调度器
scheduler.start()

while True:
    time.sleep(1)
