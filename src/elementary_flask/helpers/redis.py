__all__ = ['redis_client']

from flask import current_app, _app_ctx_stack  # noqa
from redis import Redis

REDIS_CLIENT_ATTRIBUTE_NAME = 'elementary_flask_redis_client'


def redis_client():
    ctx = _app_ctx_stack.top
    if ctx is not None:
        # current_app.teardown_appcontext(_teardown)
        if not hasattr(ctx, REDIS_CLIENT_ATTRIBUTE_NAME):
            setattr(ctx, REDIS_CLIENT_ATTRIBUTE_NAME, _redis_client())
        return getattr(ctx, REDIS_CLIENT_ATTRIBUTE_NAME)


def _redis_client():
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
                db=redis_config.get('db', 0),
            )


def _teardown(exception):
    ctx = _app_ctx_stack.top
    if ctx and hasattr(ctx, REDIS_CLIENT_ATTRIBUTE_NAME):
        getattr(ctx, REDIS_CLIENT_ATTRIBUTE_NAME).close()
