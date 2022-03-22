from libs import fetcher
from apscheduler.schedulers.background import BackgroundScheduler
import time

# 初始化后台调度器
scheduler = BackgroundScheduler(timezone='UTC')

#待跳过拉取的symbol name 
skip_symbols = ['TNX']

# 每周周日23时0分0秒到周一13时0分0秒,只更新非TNX以外的数据
#周日
# 分钟级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='sun',
    hour='23',
    minute='0-59',
    args=['1m', skip_symbols],
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
    args=['1h', skip_symbols],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

#周一
# 分钟级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='mon',
    hour='0-13',
    minute='0-59',
    args=['1m', skip_symbols],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)
#小时级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='mon',
    hour='0-13',
    args=['1h', skip_symbols],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)


# 周一13点～周五23点,同时更新yfinance和mt5的数据
#周一13点～周一23点
# 分钟级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='mon',
    hour='13-23',
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
    day_of_week='mon',
    hour='13-23',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
    )


#周二0点～周五23点
# 分钟级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='tue-fri',
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
    day_of_week='tue-fri',
    hour='0-23',
    args=['1h'],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

# 周六0点-周六3点,只更新mt5的数据
# 分钟级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='sat',
    hour='0-3',
    minute='0-59',
    args=['1m', skip_symbols],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)
# 小时级数据
scheduler.add_job(
    fetcher.update_realtime_data,
    trigger='cron',
    day_of_week='sat',
    hour='0-3',
    args=['1h', skip_symbols],
    max_instances=100,
    misfire_grace_time=60,
    coalesce=True
)

# 启动调度器
scheduler.start()

while True:
    time.sleep(1)
