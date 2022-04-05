import time
from datetime import datetime

from elementary_flask.cron import CronEntry, cron_endpoint


def hello_world(ix):
    def f(cron_context):
        print("hello", ix, cron_context)

    return f


crontab = [
    CronEntry('test0', '@daily', task=hello_world(0)),
    CronEntry('test1', '@hourly', task=hello_world(1)),
    CronEntry('test2', 'H * * * *', task=hello_world(2)),
    CronEntry('test3', 'H H * * *', task=hello_world(3)),
]

t = (int(time.time()) // 3600) * 3600
for i in range(3600):
    print(datetime.fromtimestamp(t + 60 * i), cron_endpoint(crontab, t + 60 * i))
