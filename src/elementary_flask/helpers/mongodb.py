__all__ = ['mongo_client', 'mongo_db', 'connect_mongoengine']

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


def mongo_db(db):
    return mongo_client()[db]


def _setup_mongo_config():
    elementary_config = current_app.config.setdefault('ELEMENTARY_FLASK', dict())
    mongo_config = elementary_config.get('mongodb', False)
    debug = current_app.config.get('DEBUG', True)

    if mongo_config is not False:
        if not mongo_config:
            elementary_config['mongodb'] = dict()
            mongo_config = elementary_config['mongodb']

        if 'url' not in mongo_config:
            host = mongo_config.setdefault('host', 'localhost' if debug else 'mongo')
            port = mongo_config.setdefault('port', 27017)
            db = mongo_config.setdefault('db', 'defaultdb')
            mongo_config.setdefault('url', "mongodb://%s:%d/%s" % (host, port, db))

        mongo_config.setdefault('connect_mongoengine', False)

    return mongo_config


def _mongo_client():
    import pymongo  # noqa
    mongo_config = _setup_mongo_config()

    if mongo_config:
        return pymongo.MongoClient(mongo_config['url'])


def connect_mongoengine():
    mongo_config = _setup_mongo_config()
    if mongo_config and mongo_config.get('connect_mongoengine'):
        import mongoengine  # noqa
        mongoengine.connect(host=mongo_config['url'])


def _teardown(exception):
    ctx = _app_ctx_stack.top
    if ctx and hasattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME):
        getattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME).close()
