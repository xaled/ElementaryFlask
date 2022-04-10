__all__ = ['redis_client']

from flask import current_app, _app_ctx_stack  # noqa
from redis import Redis

from elementary_flask.globals import current_elementary_flask_app

REDIS_CLIENT_ATTRIBUTE_NAME = 'elementary_flask_redis_client'


def redis_client(db=None):
    ctx = _app_ctx_stack.top
    attribute_name = REDIS_CLIENT_ATTRIBUTE_NAME + '_' + str(db)
    if ctx is not None:
        # current_app.teardown_appcontext(_teardown)
        if not hasattr(ctx, attribute_name):
            setattr(ctx, attribute_name, _redis_client())
            current_elementary_flask_app.append_teardown(_teardown(attribute_name))
        return getattr(ctx, attribute_name)


def _redis_client(db=None):
    redis_config = current_app.config.get('REDIS', False)
    debug = current_app.config.get('DEBUG', True)
    if redis_config is not False:
        redis_config = redis_config if redis_config is not None else dict()
        if 'url' in redis_config:
            return Redis.from_url(redis_config['url'])
        else:
            return Redis(
                host=redis_config.get('host', None) or ("localhost" if debug else 'redis'),
                port=redis_config.get('port', 6379),
                db=db if db is None else redis_config.get('db', 0),
            )


def _teardown(attribute_name):
    def _td(e):
        ctx = _app_ctx_stack.top
        if ctx and hasattr(ctx, attribute_name):
            getattr(ctx, attribute_name).close()

    return _td
