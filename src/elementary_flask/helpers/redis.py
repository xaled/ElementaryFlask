__all__ = ['redis_client', 'pottery_factory']

# from flask import current_app, _app_ctx_stack  # noqa
from redis import Redis, ConnectionPool
from pottery import RedisSet, RedisDict, RedisList, RedisCounter, RedisDeque, RedisSimpleQueue, Redlock, NextId, \
    redis_cache, CachedOrderedDict, BloomFilter, HyperLogLog
from pottery import ContextTimer as _ContextTimer

from .config import get_helper_config

# REDIS_CLIENT_ATTRIBUTE_NAME = 'elementary_flask_redis_client'
_AUTO_RELEASE_TIME = Redlock._AUTO_RELEASE_TIME  # noqa
_NUM_EXTENSIONS = Redlock._NUM_EXTENSIONS  # noqa
_NUM_TRIES = NextId._NUM_TRIES  # noqa
_CACHED_ORDERED_DICT_NUM_TRIES = CachedOrderedDict._NUM_TRIES  # noqa
from pottery.cache import _DEFAULT_TIMEOUT  # noqa

_redis_clients = dict()
_redis_pools = dict()


# def redis_client(db=None):
#     ctx = _app_ctx_stack.top
#     attribute_name = REDIS_CLIENT_ATTRIBUTE_NAME + '_' + str(db)
#     if ctx is not None:
#         # current_app.teardown_appcontext(_teardown)
#         if not hasattr(ctx, attribute_name):
#             setattr(ctx, attribute_name, _redis_client())
#             current_elementary_flask_app.append_teardown(_teardown(attribute_name))
#         return getattr(ctx, attribute_name)

def redis_client(db=None, config=None):
    global _redis_clients
    if db not in _redis_clients or _redis_clients[db] is None:
        _redis_clients[db] = _get_redis_client(db, config=config)
    return _redis_clients[db]


def _get_redis_client(db=None, config=None):
    global _redis_pools
    if db not in _redis_pools or _redis_pools[db] is None:
        _redis_pools[db] = _get_redis_pool(db, config=config)

    if _redis_pools[db] is None:
        return None
    return Redis(connection_pool=_redis_pools[db])


def _get_redis_pool(db=None, config=None):
    redis_config = _setup_redis_config(config=config)
    if redis_config is not False:
        redis_config = redis_config if redis_config is not None else dict()
        if 'url' in redis_config:
            return ConnectionPool.from_url(redis_config['url'])
        else:
            return ConnectionPool(
                host=redis_config['host'],
                port=redis_config['port'],
                db=db if db is not None else redis_config['db'],
            )


def _setup_redis_config(config=None):
    app_config = config or get_helper_config()
    elementary_config = app_config.setdefault('ELEMENTARY_FLASK', dict())
    redis_config = elementary_config.setdefault('redis', dict())
    debug = app_config.setdefault('DEBUG', True)

    if redis_config is not False:
        if 'url' not in redis_config:
            redis_config.setdefault('host', 'localhost' if debug else 'redis')
            redis_config.setdefault('port', 6379)
            redis_config.setdefault('db', 0)
            redis_config.setdefault(
                'key_prefix',
                app_config.setdefault('ELEMENTARY_FLASK_APP_NAME', 'test_app').upper() + '_'
            )

    return redis_config


# def _teardown(attribute_name):
#     def _td(e):
#         ctx = _app_ctx_stack.top
#         if ctx and hasattr(ctx, attribute_name):
#             getattr(ctx, attribute_name).close()
#
#     return _td


class _PotteryFactories:
    @staticmethod
    def RedisSet(iterable=tuple(), *, redis=None, key=''):  # noqa
        redis = redis or redis_client()
        if key and redis.exists(key):
            return RedisSet(redis=redis, key=key)
        return RedisSet(iterable, redis=redis, key=key)

    @staticmethod
    def RedisDict(arg=tuple(), *, redis=None, key=''):  # noqa
        redis = redis or redis_client()
        if key and redis.exists(key):
            return RedisDict(redis=redis, key=key)
        return RedisDict(arg, redis=redis, key=key)

    @staticmethod
    def RedisList(iterable=tuple(), *, redis=None, key=''):  # noqa
        redis = redis or redis_client()
        if key and redis.exists(key):
            return RedisList(redis=redis, key=key)
        return RedisList(iterable, redis=redis, key=key)

    @staticmethod
    def RedisCounter(arg=tuple(), *, redis=None, key=''):  # noqa
        redis = redis or redis_client()
        if key and redis.exists(key):
            return RedisCounter(redis=redis, key=key)
        return RedisCounter(arg, redis=redis, key=key)

    @staticmethod
    def RedisDeque(iterable=tuple(), *, redis=None, key=''):  # noqa
        redis = redis or redis_client()
        if key and redis.exists(key):
            return RedisDeque(redis=redis, key=key)
        return RedisDeque(iterable, redis=redis, key=key)

    @staticmethod
    def RedisSimpleQueue(arg, *, redis=None, key=''):  # noqa
        redis = redis or redis_client()
        return RedisSimpleQueue(redis=redis, key=key)

    @staticmethod
    def Redlock(*, masters=None, key='',  # noqa
                raise_on_redis_errors: bool = False,
                auto_release_time: float = _AUTO_RELEASE_TIME,
                num_extensions: int = _NUM_EXTENSIONS,
                context_manager_blocking: bool = True,
                context_manager_timeout: float = -1,
                ):
        masters = masters or {redis_client()}
        return Redlock(masters=masters, key=key,
                       raise_on_redis_errors=raise_on_redis_errors,
                       auto_release_time=auto_release_time,
                       num_extensions=num_extensions,
                       context_manager_blocking=context_manager_blocking,
                       context_manager_timeout=context_manager_timeout
                       )

    @staticmethod
    def NextId(*,  # noqa
               key: str = 'current', masters=None,
               raise_on_redis_errors: bool = False,
               num_tries: int = _NUM_TRIES):
        masters = masters or {redis_client()}
        return NextId(key=key, masters=masters, raise_on_redis_errors=raise_on_redis_errors, num_tries=num_tries)

    @staticmethod
    def redis_cache(  # noqa
            *, redis=None, key='',
            timeout=_DEFAULT_TIMEOUT):
        redis = redis or redis_client()
        return redis_cache(redis=redis, key=key, timeout=timeout)

    @staticmethod
    def CachedOrderedDict(*,  # noqa
                          redis=None,
                          redis_key=None,
                          dict_keys=tuple(),
                          num_tries=_CACHED_ORDERED_DICT_NUM_TRIES,
                          timeout=_DEFAULT_TIMEOUT, ):
        redis = redis or redis_client()
        return CachedOrderedDict(
            redis_client=redis,
            redis_key=redis_key,
            dict_keys=dict_keys,
            num_tries=num_tries,
            timeout=timeout, )

    @staticmethod
    def BloomFilter(iterable=frozenset(), *,  # noqa
                    num_elements: int,
                    false_positives: float,
                    redis=None, key='',
                    ):
        redis = redis or redis_client()
        return BloomFilter(iterable, num_elements=num_elements, false_positives=false_positives, redis=redis, key=key)

    @staticmethod
    def HyperLogLog(  # noqa
            iterable=frozenset(),
            *,
            redis=None,
            key=''):
        redis = redis or redis_client()
        return HyperLogLog(iterable, redis=redis, key=key)

    ContextTimer = _ContextTimer


pottery_factory = _PotteryFactories()
