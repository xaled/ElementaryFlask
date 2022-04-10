__all__ = ['mongo_client', 'mongo_db']

from flask import current_app, _app_ctx_stack  # noqa

from elementary_flask.globals import current_elementary_flask_app

MONGO_CLIENT_ATTRIBUTE_NAME = 'elementary_flask_mongo_client'


def mongo_client():
    ctx = _app_ctx_stack.top
    if ctx is not None:
        # current_app.teardown_appcontext(_teardown)
        if not hasattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME):
            setattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME, _mongo_client())
            current_elementary_flask_app.append_teardown(_teardown)
        return getattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME)


def mongo_db(dbname):
    return mongo_client()[dbname]


def _mongo_client():
    import pymongo
    mongo_config = current_app.config.get('MONGODB', False)
    debug = current_app.config.get('DEBUG', True)

    if mongo_config is not False:
        mongo_config = mongo_config if mongo_config is not None else dict()
        if 'url' in mongo_config:
            return pymongo.MongoClient(mongo_config['url'])
        else:
            return pymongo.MongoClient("mongodb://%s:27017/" % 'localhost' if debug else 'mongo')
            # return Redis(
            #     host=redis_config.get('host', None) or ("localhost" if debug else 'redis'),
            #     port=redis_config.get('port', 6379),
            #     db=redis_config.get('db', 0),
            # )


def _teardown(exception):
    ctx = _app_ctx_stack.top
    if ctx and hasattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME):
        getattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME).close()
