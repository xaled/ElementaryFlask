from croniter import croniter

from flaskly.typing import Callable


class CronEntry:
    def __init__(self, name: str, expr_format: str, /, *, task: Callable, hash_id=None, args=None, kwargs=None):
        hash_id = hash_id or name
        self.name = name
        self.croniter = croniter(expr_format, hash_id=hash_id, ret_type=float)
        self.task = task
        self.args = args or tuple()
        self.kwargs = kwargs or dict()

    def __call__(self, cron_context=None):
        return self.fire(cron_context=cron_context)

    def fire(self, cron_context=None):
        # return self.task(cron_context=cron_context, *self.args, **self.kwargs)
        return self.task(*self.args, **self.kwargs)

    def get_next(self, start_time=None):
        return self.croniter.get_next(start_time=start_time)
