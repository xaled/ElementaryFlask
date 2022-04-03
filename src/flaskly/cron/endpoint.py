import time
from datetime import datetime
from types import SimpleNamespace

from flaskly.globals import current_flaskly_app as _app
from flaskly.typing import Iterable, CronEntry

_next_jobs = dict()  # TODO must be redis server


def cron_endpoint(crontab: Iterable[CronEntry] = None, current_time: int = None):
    crontab = crontab if crontab is not None else _app.crontab
    current_time = current_time if current_time is not None else (int(time.time()) // 60) * 60
    fail, success = 0, 0

    def _fire(cn, st):
        try:
            cron_entry.fire(SimpleNamespace(cron_name=cn, scheduled_time=st, current_time=current_time))
            _next_jobs.pop(cron_name, None)
            return True
        except Exception:
            _app.logger.warning('Error executing cron: %s', cron_name, exc_info=True)
            return False

    for cron_entry in crontab:
        cron_name = cron_entry.name
        if cron_name in _next_jobs and _next_jobs[cron_name] <= current_time:
            if _fire(cron_name, _next_jobs[cron_name]):
                success += 1
            else:
                fail += 1

        elif cron_name in _next_jobs:
            pass
        else:
            nxt = int(cron_entry.get_next(current_time - 1))
            if nxt == current_time:
                if _fire(cron_name, nxt):
                    success += 1
                else:
                    fail += 1
            else:
                _next_jobs[cron_name] = nxt

    _app.logger.debug('Cron queue contains %d item: %s', len(_next_jobs),
                      tuple(f'{k}: {str(datetime.fromtimestamp(v))}' for k, v in _next_jobs.items()))
    return {'failed_tasks': fail, 'successful_tasks': success, 'total_run_tasks': fail + success,
            'tasks_waiting': len(_next_jobs)}
